import requests
import json

url = "http://143.107.145.46:1026/v2/subscriptions"

#payload = "{\n\t\"subject\": {\n\t\t\"entities\": [\n\t\t\t{\n\t\t\t\t\"id\": \"device_1\",\n\t\t\t\t\"type\": \"iot_device\"\n\t\t\t}\n\t\t\t],\n\t\t\t\"condition\": {\n\t\t\t\t\"attrs\": [\n\t\t\t\t\t\"time\"\n\t\t\t\t\t]\n\t\t\t}\n\t},\n\t\"notification\": {\n\t\t\"http\":  {\n\t\t\t\"url\": \"http://143.107.145.36:1028/accumulate\"\n\t\t}\n\t}\n}"

payload = {
    'subject': {
        'entities': [{
            'id': 'dev__id_1',
            'type': 'URLLC',
        }],
        'condition': {
            'attrs': ['time']
        }
    },
    'notification': {
        'http': {
            'url': 'http://143.107.145.36:1028/accumulate'
        }
    }
}


headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.status_code)
print(response.text)