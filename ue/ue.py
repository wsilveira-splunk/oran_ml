import requests
import json
import random
import multiprocessing
import string

from datetime import datetime

HELIX_URL = "http://143.107.145.46:1026/v2/entities/"

UE_TYPE = ['eMMB', 'mMTC', 'URLLC']
UE_PACKET_TYPE = ['plane:control', 'plane:user']

def ue_descriptor_init_rand():

    ue_descriptor = dict()
    ue_descriptor['id'] = random.randint(1, 1000)
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


def ue_creation(device_descriptor):

    payload = dict()
    payload['id'] = 'dev_id:' + str(device_descriptor['id'])
    payload['type'] = device_descriptor['type']
    payload['packet'] = dict()
    payload['packet']['type'] = device_descriptor['packet_type']
    payload['packet']['value'] = device_descriptor['packet_data']

    try:
        r = requests.post(HELIX_URL, json=payload)

        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return False, e

    return True, None

def ue_created(device_descriptor):

    url = HELIX_URL + 'dev_id:' + str(device_descriptor['id'])

    try:
        r = requests.get(url)

        r.raise_for_status()
    except:
        return False

    return True

def ue_tx_packet(device_descriptor):

    url = HELIX_URL + 'dev_id:' + str(device_descriptor['id']) + '/attrs/packet'

    try:
        r = requests.put(url, json={'value': device_descriptor['packet_data']})

        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error: {}'.format(e))
        return False

    return True

def ue_rx_packet(device_descriptor):

    url = HELIX_URL + 'dev_id:' + str(device_descriptor['id'])

    try:
        r = requests.get(url)

        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Error: {}'.format(e))
        return False, None

    return True, r.text

if __name__ == '__main__':

    for i in range(5):

        ue_descriptor = ue_descriptor_init_rand()

        if (not ue_created(ue_descriptor)):
            ret, msg = ue_creation(ue_descriptor)

            if (ret == False):
                print('Error Creating Device: {}'.format(msg))
                exit(1)
        else:
            ue_tx_packet(ue_descriptor)

        ret, msg = ue_rx_packet(ue_descriptor)
        print(json.dumps(json.loads(msg), indent=4))    