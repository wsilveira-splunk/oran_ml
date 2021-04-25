from oran import NearRealTimeRIC as RIC
from ue import UserEquipment as UE
from datetime import datetime

import json
import csv

ORAN_BASE_URL = "http://143.107.145.46:1026/v2/entities/"
DOCKER_SOCKET = 'unix://var/run/docker.sock'
DOCKER_API_VERSION = '1.40'
COLUMNS = ['TS', 'UEID', 'UETYPE', 'UEPACKETTYPE', 'UEPACKETVALUE', 'ORANSERVICE', 'ORANCPUUSAGE', 'ORANMEMUSAGE', 'ORANTXBYTES', 'ORANRXBYTES', 'ORANSCALE']

if __name__ == '__main__':
    oran = RIC(DOCKER_SOCKET, DOCKER_API_VERSION)
    ue = UE(ORAN_BASE_URL)

    ts = datetime.now().strftime('%b %d %Y %H:%M:%S')
    
    with open('oran_sim - {}.csv'.format(ts), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        while True:
            ue_info = ue.ue_simulation(5)
            ts_ue = datetime.now().strftime('%b %d %Y %H:%M:%S')

            oran_info = oran.get_NearRealTimeRIC_info()
            ts_oran = datetime.now().strftime('%b %d %Y %H:%M:%S')

            ts = datetime.now().strftime('%b %d %Y %H:%M:%S')
            for oran_service, oran_service_info in oran_info.items():
                new_row = dict()
                new_row['TS'] = ts_oran
                new_row['ORANSERVICE'] = oran_service
                new_row['ORANCPUUSAGE'] = oran_service_info['perc_cpu_usage']
                new_row['ORANMEMUSAGE'] = oran_service_info['perc_mem_usage']
                new_row['ORANTXBYTES'] = oran_service_info['tx_bytes']
                new_row['ORANRXBYTES'] = oran_service_info['rx_bytes']
                new_row['ORANSCALE'] = oran_service_info['scale']

                writer.writerow(new_row)

            for ue_id, ue_info in ue_info.items():
                new_row = dict()
                new_row['TS'] = ts_ue
                new_row['UEID'] = ue_id
                new_row['UETYPE'] = ue_info['type']
                new_row['UEPACKETTYPE'] = ue_info['packet']['type']
                new_row['UEPACKETVALUE'] = ue_info['packet']['type']

                writer.writerow(new_row)

            print(json.dumps(ue_info, indent=4))
            print(json.dumps(oran_info, indent=4))





