from oran import NearRealTimeRIC as RIC
from ue import UserEquipment as UE
from datetime import datetime, timedelta

import json
import csv

ORAN_BASE_URL = "http://143.107.145.46:1026/v2/entities/"
DOCKER_SOCKET = 'unix://var/run/docker.sock'
DOCKER_API_VERSION = '1.40'
COLUMNS = ['TS', 'UEID', 'UETYPE', 'UEPACKETTYPE', 'UEPACKETVALUE', 'ORANSERVICE', 'ORANCPUUSAGE', 'ORANMEMUSAGE', 'ORANTXBYTES', 'ORANRXBYTES', 'ORANSCALE']
MAX_NUMBER_UES = 200


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
    ts = ts.strftime('%b %d %Y %H:%M:%S')

    oran.set_NearRealTimeRIC_scale(6)

    with open('oran_sim - {}.csv'.format(ts), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        number_ues = 20
        ue_sim_file = 'ue_sim - {}.csv'.format(ts)
        ue.ue_sim_start(ue_sim_file, number_ues)

        while True:
            oran_info = oran.get_NearRealTimeRIC_info()
            ts = datetime.now()
            ts_oran = ts.strftime('%b %d %Y %H:%M:%S')

            for oran_service, oran_service_info in oran_info.items():
                new_row = dict()
                new_row['TS'] = ts_oran
                new_row['ORANSERVICE'] = oran_service
                new_row['ORANCPUUSAGE'] = oran_service_info['perc_cpu_usage']
                new_row['ORANMEMUSAGE'] = oran_service_info['perc_mem_usage']
                new_row['ORANTXBYTES'] = oran_service_info['tx_bytes']
                new_row['ORANRXBYTES'] = oran_service_info['rx_bytes']
                new_row['ORANSCALE'] = oran_service_info['scale']

                if 'orion_orion' in oran_service and oran_service != '/orion_orion.6.xt4na49uu2s3lmz47w5i4rf77': 
                    oran_info['/orion_orion.6.xt4na49uu2s3lmz47w5i4rf77']['perc_cpu_usage'] += oran_service_info['perc_cpu_usage']

                writer.writerow(new_row)

            if (ts >= step_1 and ts <= step_1_1):
                oran.set_NearRealTimeRIC_scale(8)
            elif (ts >= step_2 and ts <= step_2_1):
                oran.set_NearRealTimeRIC_scale(10)
            elif (ts >= step_3 and ts <= step_3_1):
                number_ues = 150
                ue.ue_sim_update(number_ues)

            print(json.dumps(oran_info['/mongo_mongo.n698uif6kysk59gdy3wg92men.tyrsz3jqsakrwslxbi2ze3ug9'], indent=4))
            print('Number of UEs: {}'.format(number_ues))