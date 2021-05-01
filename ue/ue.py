import json
import requests
import time
import string
import random

from datetime import datetime
from multiprocessing import Pool

DEV_ID_RANGE_MIN = 1
DEV_ID_RANGE_MAX = 2000

UE_TYPE = ['eMMB', 'mMTC', 'URLLC']
UE_PACKET_TYPE = ['plane:control', 'plane:user']

UE__ID_ = 'ue__id_{}'
UE_PACKET_ENDPOINT = '{}/{}/attrs?options=forcedUpdate' 

CONTROL_CHANNEL_MODES ={
    'CPU_CORES' : [1, 2, 3, 4],
    'POST_CALLS': [25, 50, 75, 100],
    'DELAY': [0.0075, 0.005, 0.0025, 0.001],
    'PACKET_DATA_SIZE': [1, 10, 30, 100]
}

class UserEquipment():

    def __init__(self, openran_addr):
        self.openran_addr = openran_addr
        self.ue_id_min = DEV_ID_RANGE_MIN
        self.ue_id_max = DEV_ID_RANGE_MAX

    def ue_descriptor_init_rand(self):

        random_id = random.randint(DEV_ID_RANGE_MIN, DEV_ID_RANGE_MAX)

        ue_descriptor = dict()
        ue_descriptor['id'] = UE__ID_.format(random_id)
        ue_descriptor['slice'] = {'type': 'string', 'value': UE_TYPE[random.randint(0, len(UE_TYPE) - 1)]}
        ue_descriptor['time'] = {'type': 'string', 'value': str(datetime.now().timestamp())}
        ue_descriptor['plane'] = {'type': 'string', 'value': UE_PACKET_TYPE[random.randint(0, len(UE_PACKET_TYPE) - 1)]}  

        packet_size = 0
        if (ue_descriptor['plane']['value'] == 'plane:control'):
            packet_size = 10
        elif (ue_descriptor['slice']['value'] == 'eMMB'):
            packet_size = random.randint(1000, 20000)
        elif (ue_descriptor['slice']['value'] == 'mMTC'):
            packet_size = random.randint(5, 8)
        elif (ue_descriptor['slice']['value'] == 'URLLC'):
            packet_size = random.randint(2, 4)

        packet_size = 1

        letters = string.ascii_letters
        ue_descriptor['payload']  = {'type': 'string', 'value': ''.join(random.choice(letters) for i in range(packet_size)) }
        
        return ue_descriptor
    
    def __ue_descriptor_init(self, id):
        if id < self.ue_id_min or id > self.ue_id_max:
            return False

        ue_descriptor = dict()
        ue_descriptor['id'] = UE__ID_.format(id)
        ue_descriptor['slice'] = {'type': 'string', 'value': None}
        ue_descriptor['time'] = {'type': 'string', 'value': str(datetime.now().timestamp())}
        ue_descriptor['plane'] = {'type': 'string', 'value': None}
        ue_descriptor['payload'] = {'type': 'string', 'value': None} 
        
        return ue_descriptor

    def register_device(self, device_descriptor):
        if device_descriptor['id'] < self.ue_id_min or device_descriptor['id'] > self.ue_id_max:
            print('Error, device ID out of permitted range')
            return False

        try:
            headers = {'Content-Type': 'application/json'}
            ret = requests.post(url=self.openran_addr, headers=headers, data=json.dumps(device_descriptor))

            ret.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error registering device {}: {}'.format(device_descriptor['id'], e))
            return False
        
        return True

    def register_device_pool(self, device_id_min, device_id_max):

        if device_id_min < self.ue_id_min or device_id_max > self.ue_id_max:
            print('Error, device ID out of permitted range')
            return False

        for device_id in range(device_id_min, device_id_max):
            device_descriptor = self.__ue_descriptor_init(device_id)
            try:
                headers = {'Content-Type': 'application/json'}
                ret = requests.post(url=self.openran_addr, headers=headers, data=json.dumps(device_descriptor))

                ret.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print('Error registering device {}: {}'.format(device_descriptor['id'], e))
                return False
        
        return True

    def ue_send_packet(self, device_id, plane, payload):

        if device_id < self.ue_id_min or device_id > self.ue_id_max:
            print('Error, device ID out of permitted range')
            return False

        packet = dict()
        # TODO: Need all info to update entity?
        #packet['slice'] = ??
        packet['plane'] = plane
        packet['time'] = datetime.now().strftime('%b %d %Y %H:%M:%S:%f')
        packet['payload'] = payload

        try:
            headers = {'Content-Type': 'application/json'}
            url = UE_PACKET_ENDPOINT.format(self.openran_addr, device_id)
            ret = requests.post(url=url, headers=headers, data=json.dumps(ue_desc))

            ret.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error sending packet! Device {}: {}'.format(device_id, e))
            return False
        
        return True

    def ue_read_control_channel(self):

        try:
            url = UE_PACKET_ENDPOINT.format(self.openran_addr, 'control__channel_1')
            ret = requests.get(url=url, headers={'Accept': 'application/json'})

            ret.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error getting Control Channel info: {}'.format(e))
            return False

        ret = json.loads(ret.text)

        control_channel = dict()

        for k, v in ret.items():
            if ret[k]['value'] < 1 or ret[k]['value'] > 4:
                print('Invalid Control Channel Config')
                return None 
            control_channel[k] = ret[k]['value']

        return control_channel

    def get_openran_addr(self):
        return self.openran_addr

def load_test(ue):
    while True:
        control_channel = ue.ue_read_control_channel()

        if control_channel == None:
            print('Stopping load test. Control Channel is invalid.')
            break

        parsed_control_channel = dict()
        for k, v in control_channel.items():
            parsed_control_channel[k] = CONTROL_CHANNEL_MODES[k][control_channel[k] - 1]

        print('\nLoad Test Config: ')
        print(json.dumps(parsed_control_channel, indent=4))

        for i in range(parsed_control_channel['POST_CALLS']):
            #p = Pool(parsed_control_channel['CPU_CORES'])
            #p.map(load_test_send_packet, [(ue, parsed_control_channel['PACKET_DATA_SIZE']) for i in range(parsed_control_channel['POST_CALLS'])])
            #p.terminate()
            load_test_send_packet((ue, parsed_control_channel['PACKET_DATA_SIZE']))
            time.sleep(parsed_control_channel['DELAY'])     


def load_test_send_packet(config):
    ue = config[0]
    packet_size = config[1]

    ue_descriptor = ue.ue_descriptor_init_rand()

    dev__id = ue_descriptor.pop('id')
    dev__id = 'ue__id_1'
    payload = ue_descriptor

    #payload.pop('type')
    #print(json.dumps(payload, indent=4))
    #payload['payload']['value'] = 'abah'

    try:
        headers = {'Content-Type': 'application/json'}
        url = UE_PACKET_ENDPOINT.format(ue.get_openran_addr(), dev__id)
        ret = requests.post(url=url, headers=headers, data=json.dumps(payload))

        ret.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error sending packet! Device {}: {}'.format(dev__id, e))  


if __name__ == '__main__':

    print('\n5G UE Simulator - Helix Multi-layered - UE Load Test\n')

    OPENRAN_ADDR = 'http://143.107.145.46:1026/v2/entities'
    ue = UserEquipment(OPENRAN_ADDR)

    ue.register_device_pool(1, 5)

    start_test = input('Init Load Test? [Y/n] ')

    if start_test.strip().lower() == 'y':
        print('Starting Load Test...')
        load_test(ue)
    else:
        print('Ok! See you again...')
