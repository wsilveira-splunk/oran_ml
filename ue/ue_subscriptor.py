from werkzeug.serving import WSGIRequestHandler
from flask import Flask, request, jsonify, json
from flask_restful import Resource, Api
import json
import csv
from datetime import datetime, timedelta
import timeit
import statistics

values = []

app = Flask(__name__)
api = Api(app)

class helix(Resource):
  def post(self):	    
    data = request.data 
    now = datetime.now()
    timestamp = str(datetime.timestamp(now))
    #print(data)
    payload = json.loads(data)
    departure = float(payload["data"][0]["time"]["value"])
    x = datetime.fromtimestamp(departure)#.strftime('%Y-%m-%d')
    dt = now - x 
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    values.append(ms)
    print(ms)
    #print(json.dumps(payload, indent=4))
    return '', 200

api.add_resource(helix, '/subs')

if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host = '0.0.0.0', port ='9991', threaded=True)
    print("OWD Statistics:")
    print("OWDs: ",values)
    mean = statistics.mean(values)
    print("OWD Average = {0:.3f}".format(mean),"ms")
    stdev = statistics.stdev(values)
    print("OWD STDev = {0:.3f}".format(stdev),"ms")
    median = statistics.median(values)
    print("OWD Median = {0:.3f}".format(median),"ms")
    min = min(values)
    print("OWD Min = {0:.3f}".format(min),"ms")
    max = max(values)
    print("OWD Max = {0:.3f}".format(max),"ms") 
    with open ('test.csv', 'w') as file_csv:
       rows = ['Measure', 'Value']
       write = csv.DictWriter(file_csv, fieldnames=rows, delimiter=',',lineterminator='\n')
       write.writeheader()
       write.writerow({'Measure' : 'mean', 'Value': str(mean)})
       write.writerow({'Measure' : 'stdev', 'Value': str(stdev)})
       write.writerow({'Measure' : 'median', 'Value': str(median)}) 

    with open ('test.csv', 'a') as file_csv:
       rows = ['OWD', 'Value']
       write = csv.DictWriter(file_csv, fieldnames=rows, delimiter=',',lineterminator='\n')
       write.writeheader()
       for num in range(1000):
         write.writerow({'OWD': num + 1, 'Value' : values[num]})

