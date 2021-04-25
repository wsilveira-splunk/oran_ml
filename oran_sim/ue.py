import requests
import json
import random
import multiprocessing
import string
import time

from datetime import datetime

DEV_ID_RANGE_MIN = 2500
DEV_ID_RANGE_MAX = 10000

UE_TYPE = ['eMMB', 'mMTC', 'URLLC']
UE_PACKET_TYPE = ['plane:control', 'plane:user']
DEV_ID = 'dev_id:'
ATTRS_PACKET = '/attrs/packet'

class UserEquipment():

    def __init__(self, oran_base_url):
        self.ue_list = list()
        self.oran_base_url = oran_base_url

    def ue_creation(self, device_descriptor):
        payload = dict()
        payload['id'] = DEV_ID + str(device_descriptor['id'])
        payload['type'] = device_descriptor['type']
        payload['packet'] = dict()
        payload['packet']['type'] = device_descriptor['packet_type']
        payload['packet']['value'] = device_descriptor['packet_data']

        try:
            r = requests.post(self.oran_base_url, json=payload)

            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return False, e

        # add created ue
        self.ue_list.append(payload.copy())

        return True, None

    def ue_deletion(self):
        self.ue_list = list()

    def ue_created(self, id):
        try:
            r = requests.get(self.oran_base_url + DEV_ID + str(id))
            r.raise_for_status()
        except:
            return False

        return True

    def ue_tx_packet(self, id, data):
        try:
            r = requests.put(self.oran_base_url + DEV_ID + str(id) + ATTRS_PACKET, json={'value': data})

            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error: {}'.format(e))
            return False

        return True

    def ue_rx_packet(self, id):
        try:
            r = requests.get(self.oran_base_url + DEV_ID + str(id))

            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error: {}'.format(e))
            return False, None

        return True, r.text

    def __ue_descriptor_init_rand(self):
        ue_descriptor = dict()
        ue_descriptor['id'] = random.randint(DEV_ID_RANGE_MIN, DEV_ID_RANGE_MAX)
        ue_descriptor['type'] = UE_TYPE[random.randint(0, len(UE_TYPE) - 1)]
        ue_descriptor['packet_type'] = UE_PACKET_TYPE[random.randint(0, len(UE_PACKET_TYPE) - 1)]

        packet_size = 0
        if (ue_descriptor['packet_type'] == 'plane:control'):
            packet_size = 10
        elif (ue_descriptor['type'] == 'eMMB'):
            packet_size = random.randint(100, 200)
        elif (ue_descriptor['type'] == 'mMTC'):
            packet_size = random.randint(4, 7)
        elif (ue_descriptor['type'] == 'URLLC'):
            packet_size = random.randint(2, 4)        

        letters = string.ascii_letters
        random_str = ''.join(random.choice(letters) for i in range(packet_size))
        ue_descriptor['packet_data'] = datetime.now().strftime('%b %d %Y %H:%M:%S') + ' - ' + random_str

        return ue_descriptor

    def ue_simulation(self, ue_number):

        # get multiprocessing manager to return collected info
        # in a parallel fashion
        manager = multiprocessing.Manager()
        ue_info = manager.dict()

        proc_list = []
        for i in range(ue_number):
            # run in processes fashion to collect info faster
            p = multiprocessing.Process(target=self.__ue_tx_rx, args=(ue_info, ))
            proc_list.append(p)
            p.start()

        for proc in proc_list:
            # join and kill the process
            proc.join()
            proc.terminate()

        self.ue_deletion()

        return ue_info.copy()

    def __ue_tx_rx(self, ue_msg):
        ue_descriptor = self.__ue_descriptor_init_rand()

        if (not self.ue_created(ue_descriptor['id'])):
            ret, msg = self.ue_creation(ue_descriptor)

            if (ret == False):
                print('Error Creating Device: {}'.format(msg))
                # TODO: improve this
        else:
            self.ue_tx_packet(ue_descriptor['id'], ue_descriptor['packet_data'])

        ret, msg = self.ue_rx_packet(ue_descriptor['id'])

        msg = json.loads(msg)
        # avoid duplicated info
        msg_id = msg.pop('id')

        ue_msg[msg_id] = msg

