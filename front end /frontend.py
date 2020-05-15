from flask import Flask, jsonify
from flask_caching import Cache

import requests
import json
import csv

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


#CACHE_TYPE is simple which means that Will use in memory pickle and is recommended only for single process development server .
#http://brunorocha.org/python/flask/using-flask-cache.html

# IP address and port number of Catalog server.
catalogIp = "192.168.1.205"
catalogPort = 5000
# IP address and port number of Order server.
orderIp = "192.168.1.222"
orderPort = 5000


@app.route('/')
def main():
    return "FrontEnd Server"

# Query database by topics :
# 1- distributed_systems
# 2- graduate_school

@app.route('/search/<topic>', methods=['GET'])
@cache.memoize()
#The theory behind memoization is that if you have a function you need to call several times in one request .
#https://pythonhosted.org/Flask-Cache
def searchRequest(topic):
    print("Received client search request for books on topic- {}".format(topic))
    print("Sending subject-based query to the catalog server.")
    r = requests.get(
        'http://{}:{}/query_by_subject/{}'.format(catalogIp, catalogPort, topic))
 
    r = json.loads(r.text)
    print("Forwarding query results to the client.")
    return jsonify(r)
     

@app.route('/lookup/<int:item_number>', methods=['GET'])
@cache.memoize()
def lookupRequest(item_number):
    print("Received client lookup request book number {}.".format(item_number))
    print("Sending item query to the catalog server.")
    m = requests.get(
        'http://{}:{}/query_by_item/{}'.format(catalogIp, catalogPort, item_number))
    print("Lookup : Name : {} ,Stock : {} ,Cost :{}$".format(
    m.json()['title'], m.json()['stock'], m.json()['cost']))
    m = json.loads(m.text)
    print("Forwarding query results to the client.")
    return jsonify(m)


@app.route('/buy/<int:item_number>', methods=['GET'])
@cache.memoize()
#The theory behind memoization is that if you have a function you need to call several times in one request .
#https://pythonhosted.org/Flask-Cache
def buy(item_number):
    print("Client wants to buy book number {}".format(item_number))
    print("Sending buy request to the order server.")
    n = requests.get(
        'http://{}:{}/buy/{}'.format(orderIp, orderPort, item_number))
    response = json.loads(n.text)
    return jsonify(response)
 

if __name__ == '__main__':
    app.run()