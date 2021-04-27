import requests
import json
import random
import multiprocessing
import string
import time
import csv

from datetime import datetime
from multiprocessing import Pool

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
        self.unused_ues = list()
        self.csv_writer = None

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
        self.unused_ues = list()
        for i in range(DEV_ID_RANGE_MIN, self.max_number_ues - 1):
            print('Initializing device dev_id:{}'.format(i))

            ue_descriptor = self.__ue_descriptor_init_rand()
            ue_descriptor['id'] = i

            self.ue_delete(ue_descriptor['id'])
            if (not self.ue_created(ue_descriptor['id'])):
                ret, msg = self.ue_creation(ue_descriptor)

                if ret == False:
                    self.unused_ues.append(i)
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
        ue_descriptor['id'] = 1
        ue_descriptor['type'] = 'eMMB'
        ue_descriptor['packet_type'] = 'plane:user'
        ue_descriptor['packet_data'] = 'abcdv'

        return ue_descriptor

    def ue_sim_start(self, csv_file, csv_mode, number_ues):
        self.number_ues = number_ues
        self.csv_file = csv_file

        with open(self.csv_file, csv_mode) as f:
            self.csv_writer = csv.DictWriter(f, fieldnames=COLUMNS)
            if csv_mode == 'w':
                self.csv_writer.writeheader()

        self.sim_proc = multiprocessing.Process(target=self.__ue_sim)
                
        self.sim_proc.start()


    def ue_sim_update(self, number_ues):      
        self.number_ues = number_ues
        self.sim_proc.terminate()
        self.ue_sim_start(self.csv_file, 'a', self.number_ues)

    def __ue_sim(self):
        while True:
            self.ue_simulation() 

        self.sim_proc.join()
        self.sim_proc.terminate()

    def ue_simulation(self):

        ue_descriptor_list = [self.__ue_descriptor_init_rand() for i in range(10)]
        print('exe')

        p = Pool(10)
        #p.map(self.__ue_tx_rx, ue_descriptor_list)

    def __ue_tx_rx(self, ue_descriptor):

        ret = self.ue_tx_packet(ue_descriptor['id'], ue_descriptor['packet_data'])

        if ret == False:
            ue_descriptor['type'] = 'error'
        else:
            ret, msg = self.ue_rx_packet(ue_descriptor['id'])
            
            if ret == False:
                ue_descriptor['type'] = 'error'

        new_row = dict()
        new_row['TS'] = datetime.now().strftime('%b %d %Y %H:%M:%S')
        new_row['UEID'] = ue_descriptor['id']
        new_row['UETYPE'] = ue_descriptor['type']
        if ue_data['type'] != 'error':
            new_row['UEPACKETTYPE'] = ue_descriptor['packet_type']
            new_row['UEPACKETVALUE'] = ue_descriptor['packet_value']

        print('writing')
        self.writer.writerow(new_row)



