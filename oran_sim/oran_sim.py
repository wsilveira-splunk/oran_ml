from oran import NearRealTimeRIC as RIC
from ue_v2 import UserEquipment as UE
from datetime import datetime, timedelta

from collections import OrderedDict

import json
import csv
import time

ORAN_BASE_URL = "http://143.107.145.46:1026/v2/entities/"
DOCKER_SOCKET = 'unix://var/run/docker.sock'
DOCKER_API_VERSION = '1.40'
COLUMNS = ['TS', 'UEID', 'UETYPE', 'UEPACKETTYPE', 'UEPACKETVALUE', 'ORANSERVICE', 'ORANCPUUSAGE', 'ORANAVGCPUUSAGE', 'ORANSERVICES','ORANMEMUSAGE', 'ORANTXBYTES', 'ORANRXBYTES', 'ORANSCALE']
MAX_NUMBER_UES = 50


if __name__ == '__main__':
    oran = RIC(DOCKER_SOCKET, DOCKER_API_VERSION)
    ue = UE(ORAN_BASE_URL, MAX_NUMBER_UES)

    ue.ue_create_all()
    
    ts = datetime.now()
    step_1 = ts + timedelta(seconds=30)
    step_1_1 = step_1 + timedelta(seconds=5)
    step_2 = step_1 + timedelta(seconds=30)
    step_2_1 = step_2 + timedelta(seconds=5)
    step_3 = step_2 + timedelta(seconds=30)
    step_3_1 = step_3 + timedelta(seconds=5)
    step_4 = step_3 + timedelta(seconds=30)
    step_4_1 = step_4 + timedelta(seconds=5)
    ts = ts.strftime('%b %d %Y %H:%M:%S')

    oran.set_NearRealTimeRIC_scale(10)

    update = False

    with open('oran_sim - {}.csv'.format(ts), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        number_ues = 1
        ue_sim_file = 'ue_sim - {}.csv'.format(ts)
        ue.ue_sim_start(ue_sim_file, 'w', number_ues)

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
                #oran_info['/orion_orion.7.sy10y1917i4zyxe6h5qcz0i0i']['perc_cpu_usage'] = oran_info['/orion_orion.7.sy10y1917i4zyxe6h5qcz0i0i']['perc_cpu_usage'] / count
            
            writer.writerow({'TS': ts_oran, 'ORANAVGCPUUSAGE': oran_info['avg_perc_cpu_usage'], 'ORANSERVICES': oran_info['count_perc_cpu_usage']})

            if (ts >= step_1 and ts <= step_1_1):
                #oran.set_NearRealTimeRIC_scale(8)
                number_ues += 2
                #ue.ue_sim_stop()
                #time.sleep(0.5)
                #ue.ue_sim_update(number_ues)
                print('update')
                ue.ue_sim_update(number_ues)
                step_1 += timedelta(seconds=10)
                step_1_1 += timedelta(seconds=10)
            '''
            elif (ts >= step_2 and ts <= step_2_1):
                #oran.set_NearRealTimeRIC_scale(10)
            elif (ts >= step_3 and ts <= step_3_1):
                if not update:
                    update = True
                    #number_ues = 20
                    #ue.ue_sim_stop()
                    #time.sleep(0.5)
                    #ue.ue_sim_update(number_ues)
            elif (ts >= step_4 and ts <= step_4_1):
                #oran.set_NearRealTimeRIC_scale(12)
            '''

            oran_info = OrderedDict(sorted(oran_info.items()))

            print(json.dumps(oran_info, indent=4))
            print('Number of UEs: {}'.format(number_ues))
            #exit(1)