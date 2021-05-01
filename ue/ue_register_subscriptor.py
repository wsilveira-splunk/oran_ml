import requests
import json

url = "http://143.107.145.46:1026/v2/subscriptions"

payload = {
    'subject': {
        'entities': [{
            'id': 'ue__id_1',
        }],
        'condition': {
            'attrs': ['time']
        }
    },
    'notification': {
        'http': {
            'url': 'http://143.107.145.36:9991/subs'
        }
    }
}


headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.status_code)
print(response.text)