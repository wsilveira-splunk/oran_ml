from oran import NearRealTimeRIC as RIC
from ue_v2 import UserEquipment as UE
from datetime import datetime, timedelta

from collections import OrderedDict

import requests
import json
import csv
import time

ORAN_BASE_URL = "http://143.107.145.46:1026/v2/entities/"
DOCKER_SOCKET = 'unix://var/run/docker.sock'
DOCKER_API_VERSION = '1.40'
COLUMNS = ['TS', 'UEID', 'UETYPE', 'UEPACKETTYPE', 'UEPACKETVALUE', 'ORANSERVICE', 'ORANCPUUSAGE', 'ORANAVGCPUUSAGE', 'ORANSERVICES','ORANMEMUSAGE', 'ORANTXBYTES', 'ORANRXBYTES', 'ORANSCALE']
MAX_NUMBER_UES = 50

ORAN_CONTROL_CHANNEL_UPT_ATTR = ORAN_BASE_URL + 'control__channel_1/attrs?options=forcedUpdate'

def update_control_channel():
    payload = {
        'CPU_CORES': {
            'type': 'int',
            'value': 2
        },
        'POST_CALLS': {
            'type': 'int',
            'value': 0
        },
        'DELAY': {
            'type': 'int',
            'value': 0
        },
        'PACKET_DATA_SIZE': {
            'type': 'int',
            'value': 0
        }
    }

    response = requests.request("POST",
                                ORAN_CONTROL_CHANNEL_UPT_ATTR,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload))

    if response.status_code == 201:
        print('Successfully Updated Control Channel')
    else:
        print('Error Updating Control Channel: {}'.format(response.text))


if __name__ == '__main__':
    oran = RIC(DOCKER_SOCKET, DOCKER_API_VERSION)
    
    ts = datetime.now()
    temp_stab = ts

    count_scale_down = 0
    count_scale_up = 0

    oran.set_NearRealTimeRIC_scale(6)

    with open('oran_sim - {}.csv'.format(ts.strftime('%b %d %Y %H:%M:%S')), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        while True:
            oran_info = oran.get_NearRealTimeRIC_info()
            ts = datetime.now()
            ts_oran = ts.strftime('%b %d %Y %H:%M:%S')

            count_perc_cpu_usage = 0
            avg_perc_cpu_usage = 0
            for oran_service, oran_service_info in oran_info.items():
                new_row = dict()
                new_row['TS'] = ts_oran
                new_row['ORANSERVICE'] = oran_service
                new_row['ORANCPUUSAGE'] = oran_service_info['perc_cpu_usage']
                new_row['ORANMEMUSAGE'] = oran_service_info['perc_mem_usage']
                new_row['ORANTXBYTES'] = oran_service_info['tx_bytes']
                new_row['ORANRXBYTES'] = oran_service_info['rx_bytes']
                new_row['ORANSCALE'] = oran_service_info['scale']
                
                if 'orion_orion' in oran_service: 
                    avg_perc_cpu_usage += oran_service_info['perc_cpu_usage']                    
                    count_perc_cpu_usage = count_perc_cpu_usage + 1                

                writer.writerow(new_row)
            
            oran_info['count_perc_cpu_usage'] = count_perc_cpu_usage
            oran_info['avg_perc_cpu_usage'] = avg_perc_cpu_usage

            if count_perc_cpu_usage > 0:
                oran_info['avg_perc_cpu_usage'] = round(avg_perc_cpu_usage / count_perc_cpu_usage, 2)
            
            writer.writerow({'TS': ts_oran, 'ORANAVGCPUUSAGE': oran_info['avg_perc_cpu_usage'], 'ORANSERVICES': oran_info['count_perc_cpu_usage']})

            if ts > temp_stab:
                if oran_info['avg_perc_cpu_usage'] > 1.5:
                    count_scale_up += 1
                    count_scale_down = 0
                elif oran_info['avg_perc_cpu_usage'] < 0.9 and oran_info['avg_perc_cpu_usage'] > 0.1:
                    count_scale_down += 1
                    count_scale_up = 0
                
            if count_scale_up > 3:
                oran.set_NearRealTimeRIC_scale(oran.get_NearRealTimeRIC_scale() + 2)
                count_scale_up = 0
                temp_stab = ts + timedelta(seconds=5)
            elif count_scale_down > 3:
                oran.set_NearRealTimeRIC_scale(oran.get_NearRealTimeRIC_scale() - 2)
                count_scale_down = 0
                temp_stab = ts + timedelta(seconds=5)

            oran_info = OrderedDict(sorted(oran_info.items()))

            print(json.dumps(oran_info['/mongo_controller.1.bqcp6ca7ytfrz3l3dc2enwxu3']['scale'], indent=4))
            print(json.dumps(oran_info['avg_perc_cpu_usage'], indent=4))
            print(json.dumps(oran_info, indent=4))
            print('Count up: {} Count down: {}'.format(count_scale_up, count_scale_down))
            print('ts: {} temp_stab: {}'.format(ts, temp_stab))
            #print('Number of UEs: {}'.format(number_ues))
            #exit(1)
