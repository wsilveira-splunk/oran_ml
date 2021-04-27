import json
import requests
import time
import timeit
import multiprocessing

from datetime import datetime
from requests import Request, Session
from multiprocessing import Pool


UE_DEVICE_ID = 'dev__id_1'

ORAN_BASE_URL = 'http://143.107.145.46:1026/'
ORAN_ENTITIES_URL = ORAN_BASE_URL + 'v2/entities'
ORAN_DEVICE_UPT_ATTR = ORAN_BASE_URL + 'v2/entities/' + UE_DEVICE_ID + '/attrs?options=forcedUpdate'
ORAN_VERSION = ORAN_BASE_URL + '/version'
ORAN_DEVICE_UPT_ATTR_PACKET = ORAN_BASE_URL + 'v2/entities/' + UE_DEVICE_ID + '/attrs/packet/value?options=forcedUpdate'


url1 = "http://143.107.145.46:1026/v2/entities"
url2 = "http://143.107.145.46:1026/v2/entities/device_1/attrs?options=forcedUpdate"
url3 = "http://143.107.145.46:1026/version"
url4 = "http://143.107.145.46:1026/v2/entities/device_1/attrs/time/value?options=forcedUpdate"


def create(url):
    payload_create = {
        'id': UE_DEVICE_ID,
        'type': 'URLLC',
        'packet': {
            'type': 'string',
            'value': 'abcdcd'
        },
        'time': {
            'type': 'float',
            'value': str(datetime.now().timestamp())
        }
    }
    
    #payload_create = "{\r\n  \"id\": \"device_1\",\r\n  \"type\": \"iot_device\",\r\n  \"temperature\": {\r\n  \"type\": \"float\",\r\n  \"value\": 0\r\n    }\r\n,\r\n  \"time\": {\r\n  \"type\": \"float\",\r\n  \"value\": 0\r\n\t}\r\n}\r\n\r\n  \r\n"

    response = requests.request("POST",
                                url,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_create))
                                #data=payload_create)
    #data=payload_create)

    if response.status_code == 201:
        print('Successfully Created')
    else:
        print('Error Creating device: {}'.format(response.text))


def update_post(url, temperature, time):
    payload_update = {
        'packet': {
            'type': 'string',
            'value': 'abcdcd'
        },
        'time': {
            'type': 'float',
            'value': str(timestamp = datetime.now().timestamp())
        }
    }

    #payload_update = "{\r\n  \"temperature\": {\r\n  \"type\": \"float\",\r\n  \"value\":" + temperature + "\r\n    }\r\n,\r\n  \"time\": {\r\n  \"type\": \"float\",\r\n  \"value\":" + time + "\r\n\t}\r\n}\r\n"

    response = requests.request("POST",
                                url,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_update))
                                #data=payload_update)
    #data=payload_update)
    if response.status_code >= 400:
        print('Error updating device: {}'.format(response.text))

def update_post_pool(time):
    payload_update = {
        'packet': {
            'type': 'string',
            'value': 'abcdcd'
        },
        'time': {
            'type': 'float',
            'value': time
        }
    }

    #payload_update = "{\r\n  \"temperature\": {\r\n  \"type\": \"float\",\r\n  \"value\":" + temperature + "\r\n    }\r\n,\r\n  \"time\": {\r\n  \"type\": \"float\",\r\n  \"value\":" + time + "\r\n\t}\r\n}\r\n"

    response = requests.request("POST",
                                ORAN_DEVICE_UPT_ATTR,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_update))
                                #data=payload_update)
    #data=payload_update)
    if response.status_code >= 400:
        print('Error updating device: {}'.format(response.text))

def get(url):

    start = timeit.default_timer()

    response = requests.request("GET",
                                url,
                                headers={'Accept': 'application/json'},
                                data={})
    stop = timeit.default_timer()
    rtt = stop - start
    print("\nTime - timeit (s): ", rtt, "\n")
    d = json.loads(response.text.encode('utf8'))
    print("\nResponse: ", d, "\n")


def health(url):

    start = timeit.default_timer()
    response = requests.request("GET", 
                                url, 
                                headers={}, 
                                data={})
    stop = timeit.default_timer()
    rtt = stop - start
    print("\nTime - timeit (s): ", rtt, "\n")
    d = json.loads(response.text.encode('utf8'))
    print("\nResponse: ", d, "\n")


while 1:
    print("Helix Multi-layered Mockup - IoT TX Departure\n")
    print("1 - Create Entity")
    print("2 - Update Entity")
    print("3 - Get Entity")
    print("4 - Health Check - Orion Version")
    print("5 - POST - no persistent OLD")
    print("6 - POST - persistent    OLD")
    print("7 - PUT  - persistent    NEW")
    print("8 - POST - persistent    NEW")
    print("9 - POST - pool of workers")
    print("0 - Exit")
    number = input("Choose an option: ")
    op = int(number)
    if op == 1:
        #create(url1)
        create(ORAN_ENTITIES_URL)
    elif op == 2:
        data_1 = '0' #input("Temperature: ")
        now = datetime.now()
        timestamp = str(now.timestamp())
        #update_post(url2, data_1, timestamp)
        update_post(ORAN_DEVICE_UPT_ATTR, data_1, timestamp)
        print("Timestamp: ", timestamp)

    elif op == 3:
        #get(url2)
        get(ORAN_DEVICE_UPT_ATTR)

    elif op == 4:
        #health(url3)
        health(ORAN_VERSION)

    elif op == 5:
        temperature = str(0)
        for num in range(1000):
            now = datetime.now()
            timestamp = str(now.timestamp())
            #update_post(url2, temperature, timestamp)
            update_post(ORAN_DEVICE_UPT_ATTR, temperature, timestamp)
            time.sleep(0.001)
            #print(num)
    elif op == 6:
        temperature = str(0)
        requests = requests.session()
        for num in range(1000):
            now = datetime.now()
            timestamp = str(now.timestamp())
            #update_post(url2, temperature, timestamp)
            update_post(ORAN_DEVICE_UPT_ATTR, temperature, timestamp)
            time.sleep(0.010)
            #print(num)

    elif op == 7:
        temperature = str(0)
        s = Session()
        for num in range(1000):
            now = datetime.now()
            timestamp = str(now.timestamp()) + ' - abcd'
            prepped = Request("PUT", 
                              #url4, 
                              ORAN_DEVICE_UPT_ATTR_PACKET,
                              headers={'Content-Type': 'text/plain'},
                              data=timestamp).prepare()
            resp = s.send(prepped)
            #print(resp.status_code)
            time.sleep(0.001)
            #print(num)

    elif op == 8:
        temperature = str(0)
        headers = {'Content-Type': 'application/json'}
        s = Session()
        for num in range(1000):
            now = datetime.now()
            timestamp = str(now.timestamp())
            payload_update = {
                'packet': {
                    'type': 'string',
                    'value': 'abcd'
                },
                #'temperature': {
                #    'type': 'float',
                #    'value': temperature
                #},
                'time': {
                    'type': 'float',
                    'value': timestamp
                }
            }

            prepped = Request("POST",
                              #url2,
                              ORAN_DEVICE_UPT_ATTR,
                              headers=headers,
                              data=json.dumps(payload_update)).prepare()
            resp = s.send(prepped)
            #print(resp.status_code)
            time.sleep(0.1)
            #print(num)

    elif op == 9:
        input_range = input('Enter Number of Posts: ')
        input_cpu = input('CPU CORES: ')
        timestamp = datetime.now().timestamp()
        timestamp_list = [str(timestamp + i) for i in range(int(input_range))]
        print(timestamp_list)
        print(multiprocessing.cpu_count())
        for i in range(10):
            p = Pool(int(input_cpu))
            p.map(update_post_pool, timestamp_list)
            time.sleep(0.001)
    else:
        break
