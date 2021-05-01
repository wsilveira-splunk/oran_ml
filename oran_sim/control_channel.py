import requests
import json
import time

ORAN_BASE_URL = 'http://143.107.145.46:1026/'
ORAN_ENTITIES_URL = ORAN_BASE_URL + 'v2/entities'

ORAN_CONTROL_CHANNEL_UPT_ATTR = ORAN_ENTITIES_URL + '/control__channel_1/attrs?options=forcedUpdate'

def create_control_channel():
    payload_create = {
        'id': 'control__channel_1',
        'type': 'control_channel',
        'CPU_CORES': {
            'type': 'int',
            'value': 0
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
                                ORAN_ENTITIES_URL,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_create))

    if response.status_code == 201:
        print('Successfully Created Control Channel')
    else:
        print('Error Creating Control Channel: {}'.format(response.text))

def update_control_channel(cores, post_calls, delay, data_size):
    payload_create = {
        'CPU_CORES': {
            'type': 'int',
            'value': cores
        },
        'POST_CALLS': {
            'type': 'int',
            'value': post_calls
        },
        'DELAY': {
            'type': 'int',
            'value': delay
        },
        'PACKET_DATA_SIZE': {
            'type': 'int',
            'value': data_size
        }
    }

    response = requests.post(url=ORAN_CONTROL_CHANNEL_UPT_ATTR,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(payload_create))

    print(response.status_code)

    if response.status_code == 204:
        print('Successfully Updated Control Channel')
    else:
        print('Error Updating Control Channel: {}'.format(response.text))

def get_control_channel():

    response = requests.request("GET",
                                ORAN_CONTROL_CHANNEL_UPT_ATTR,
                                headers={'Accept': 'application/json'},
                                data={})

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print('Error Getting Control Channel: {}'.format(response.text))
        return None

if __name__ == '__main__':
    while True:
        print("\n5G UE Simulator - Helix Multi-layered - Control Channel\n")
        print("1 - Create Control Channel")
        print("2 - Update Control Channel")
        print("3 - Run Update Control Channel Sequence")
        print("4 - Get Control Channel")
        print("0 - Exit")
        number = input("Choose an option: ")
        op = int(number)

        if op == 1:
            create_control_channel()

        elif op == 2:
            cores = int(input("Number of Cores [1-4]: "))
            post_calls = int(input("Number of Post Calls [1-4]: "))
            delay = int(input("Delay option [1-4]: "))
            data_size = int(input("Data size [1-4]: "))
            update_control_channel(cores, post_calls, delay, data_size)

        elif op == 3:
            sequence = [
                [1, 2, 0, 2], # 0
                [3, 3, 0, 3], # 1
                [3, 3, 0, 3], # 2
                [1, 3, 0, 3], # 3
                [0, 0, 3, 0], # 4
                [0, 3, 0, 2], # 5
                [1, 2, 1, 2], # 6
                [0, 0, 0, 0], # 7
                [2, 3, 3, 0], # 8
                [1, 1, 3, 3], # 9
                [3, 3, 0, 3], # 10
                [0, 0, 3, 0], # 11
                [1, 2, 2, 2], # 12
                [3, 3, 3, 3], # 13
                [1, 1, 1, 1], # 14
                [1, 2, 3, 3], # 15
                [0, 3, 0, 3], # 16
                [3, 0, 3, 0], # 17
                [1, 0, 0, 0], # 18
                [1, 3, 0, 3], # 19
                [2, 3, 0, 3], # 20
                [1, 0, 0, 0], # 21
                [3, 2, 1, 0], # 22
                [0, 1, 2, 3], # 23
                [0, 0, 0, 0], # 24
                [2, 0, 0, 3], # 25
                [1, 1, 1, 1], # 26
                [2, 2, 2, 2], # 27
                [2, 2, 2, 2], # 28
                [3, 3, 3, 3] # 29
            ]

            for i in range(30): # 15 minutos
                cores = sequence[i][0]
                post_calls = sequence[i][0]
                delay = sequence[i][0]
                data_size = sequence[i][0]
                update_control_channel(cores, post_calls, delay, data_size)
                print(sequence[i])
                time.sleep(30)

        elif op == 4:
            op_mode_desc = get_control_channel()
            print(json.dumps(op_mode_desc, indent=4))
        else:
            break