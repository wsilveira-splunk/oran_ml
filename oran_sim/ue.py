import requests
import json
import random
import multiprocessing
import string
import time
import csv

from datetime import datetime

DEV_ID_RANGE_MIN = 1
DEV_ID_RANGE_MAX = 2000

COLUMNS = ['TS', 'UEID', 'UETYPE', 'UEPACKETTYPE', 'UEPACKETVALUE', 'ORANSERVICE', 'ORANCPUUSAGE', 'ORANMEMUSAGE', 'ORANTXBYTES', 'ORANRXBYTES', 'ORANSCALE']
UE_TYPE = ['eMMB', 'mMTC', 'URLLC']
UE_PACKET_TYPE = ['plane:control', 'plane:user']
DEV_ID = 'dev_id:'
ATTRS_PACKET = '/attrs/packet'

class UserEquipment():

    def __init__(self, oran_base_url, max_number_ues):
        self.ue_list = list()
        self.oran_base_url = oran_base_url
        self.max_number_ues = max_number_ues
        self.number_ues = None
        self.csv_file = None
        self.sim_proc = None
        self.run_sim = False

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

    def ue_create_all(self):
        for i in range(DEV_ID_RANGE_MIN, self.max_number_ues - 1):
            print('Initializing device dev_id:{}'.format(i))

            ue_descriptor = self.__ue_descriptor_init_rand()
            ue_descriptor['id'] = i

            self.ue_delete(ue_descriptor['id'])
            if (not self.ue_created(ue_descriptor['id'])):
                ret, msg = self.ue_creation(ue_descriptor)

                if ret == False:
                    print('Error creating device dev_id:{} {}'.format(i, msg))
                    print(json.dumps(ue_descriptor, indent=4))

    def ue_deletion(self):
        self.ue_list = list()

    def ue_delete(self, id):
        try:
            r = requests.delete(self.oran_base_url + DEV_ID + str(id))
            r.raise_for_status()
        except:
            return False

        return True

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
            #print('Error: {}'.format(e))
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
        ue_descriptor['id'] = random.randint(DEV_ID_RANGE_MIN, self.max_number_ues - 1)
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
        ue_descriptor['packet_data'] = datetime.now().strftime('%b %d %Y %H:%M:%S:%f') + ' - ' + random_str

        return ue_descriptor

    def ue_sim_start(self, csv_file, number_ues):
        self.number_ues = number_ues
        self.csv_file = csv_file
        self.sim_proc = multiprocessing.Process(target=self.__ue_sim)

        with open(self.csv_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
        
        self.run_sim = True
        self.sim_proc.start()

    def ue_sim_stop(self):      
        self.run_sim = False

    def ue_sim_update(self, number_ues):      
        self.number_ues = number_ues

    def __ue_sim(self):
        while self.run_sim:
            with open(self.csv_file, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                ue_info = self.ue_simulation()
                ts_ue = datetime.now().strftime('%b %d %Y %H:%M:%S')

                for ue_id, ue_data in ue_info.items():
                    new_row = dict()
                    new_row['TS'] = ts_ue
                    new_row['UEID'] = ue_id
                    new_row['UETYPE'] = ue_data['type']
                    if ue_data['type'] != 'error':
                        new_row['UEPACKETTYPE'] = ue_data['packet']['type']
                        new_row['UEPACKETVALUE'] = ue_data['packet']['value']

                    writer.writerow(new_row)

                #print(json.dumps(ue_info, indent=4))
        
        self.sim_proc.stop()
        self.sim_proc.terminate()

    def ue_simulation(self):

        # get multiprocessing manager to return collected info
        # in a parallel fashion
        manager = multiprocessing.Manager()
        ue_info = manager.dict()

        proc_list = []
        for i in range(self.number_ues):
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

        '''
        if (not self.ue_created(ue_descriptor['id'])):
            ret, msg = self.ue_creation(ue_descriptor)

            if (ret == False):
                print('Error Creating Device: {}'.format(msg))
                # TODO: improve this
                exit(1)
        else:
            self.ue_tx_packet(ue_descriptor['id'], ue_descriptor['packet_data'])
        '''

        ret = self.ue_tx_packet(ue_descriptor['id'], ue_descriptor['packet_data'])

        #ret, msg = self.ue_rx_packet(ue_descriptor['id'])

        if ret == False:
            ue_msg[ue_descriptor['id']] = {'type': 'error'}
        else:
            ret, msg = self.ue_rx_packet(ue_descriptor['id'])

            #ue_descriptor['packet'] = {}
            #ue_descriptor['packet']['type'] = ue_descriptor.pop('packet_type')
            #ue_descriptor['packet']['value'] = ue_descriptor.pop('packet_data')
            #msg = ue_descriptor
            # avoid duplicated info
            #msg_id = msg.pop('id')

            
            if ret == False:
                ue_msg[ue_descriptor['id']] = {'type': 'error'}
            
            
            msg = json.loads(msg)
            # avoid duplicated info
            msg_id = msg.pop('id')

            ue_msg[msg_id] = msg


