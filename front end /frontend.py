from flask import Flask, jsonify
import requests
import json
import csv

app = Flask(__name__)

#CACHE_TYPE is simple which means that Will use in memory pickle and is recommended only for single process development server .
#http://brunorocha.org/python/flask/using-flask-cache.html

# IP address and port number of Catalog 1 server.
catalogIp = "192.168.1.205"
catalogPort = 5000
# IP address and port number of Catalog 2 server.
catalogIp2 = "192.168.1.182"
catalogPort2 = 5000
# IP address and port number of Order 1 server.
orderIp = "192.168.1.222"
orderPort = 5000
# IP address and port number of Order 2 server.
orderIp2 = "192.168.1.149"
orderPort2 = 5000

currentOrderServer = 0	 
flagsOrderServer = {}		 
flagsOrderServer['order1'] = 1
flagsOrderServer['order2'] = 1 
currentCatalogServer = 0	 
flagsCatalogServer = {}	
flagsCatalogServer['catalog1'] = 1
flagsCatalogServer['catalog2'] = 1 
@app.route('/')
def main():
    return "FrontEnd Server"

# Query database by topics :
# 1- distributed_systems
# 2- graduate_school

@app.route('/search/<topic>', methods=['GET'])

 #The theory behind memoization is that if you have a function you need to call several times in one request .
#https://pythonhosted.org/Flask-Cache
def searchRequest(topic):
        #Round robin
    global currentCatalogServer, flagsCatalogServer
    chooseCatalog=''
    if currentCatalogServer == 0 and flagsCatalogServer['catalog1'] == 1:
        chooseCatalog='1'
        currentCatalogServer = 1
        url = 'http://{}:{}/query_by_subject/{}'.format(catalogIp, catalogPort, topic) 
    elif flagsCatalogServer['catalog2']==1 :
        chooseCatalog ='2'
        currentCatalogServer = 0
        url = 'http://{}:{}/query_by_subject/{}'.format(catalogIp2, catalogPort2, topic) 
    else :
        chooseCatalog ='1'
        currentCatalogServer = 1
        url = 'http://{}:{}/query_by_subject/{}'.format(catalogIp, catalogPort, topic) 
        
    print("Received client search request for books on topic- {}".format(topic))
    print("Sending subject-based query to the catalog server{}.".format(chooseCatalog))
    r = requests.get(url)
 
    r = json.loads(r.text)
    print("Forwarding query results to the client.")
    return jsonify(r)
     

@app.route('/lookup/<int:item_number>', methods=['GET'])

def lookupRequest(item_number):
    #Round robin
    global currentCatalogServer, flagsCatalogServer
    chooseCatalog=''
    if currentCatalogServer == 0 and flagsCatalogServer['catalog1'] == 1:
        chooseCatalog='1'
        currentCatalogServer = 1
        url = 'http://{}:{}/query_by_item/{}'.format(catalogIp, catalogPort, item_number) 
    elif flagsCatalogServer['catalog2']==1 :
        chooseCatalog ='2'
        currentCatalogServer = 0
        url = 'http://{}:{}/query_by_item/{}'.format(catalogIp2, catalogPort2, item_number) 
    else :
        chooseCatalog ='1'
        currentCatalogServer = 1
        url = 'http://{}:{}/query_by_item/{}'.format(catalogIp, catalogPort, item_number) 

    print("Received client lookup request book number {}.".format(item_number))
    print("Sending item query to the catalog server {}.".format(chooseCatalog))
    m = requests.get(url)
    print("Lookup : Name : {} ,Stock : {} ,Cost :{}$".format(
    m.json()['title'], m.json()['stock'], m.json()['cost']))
    m = json.loads(m.text)
    print("Forwarding query results to the client.")
    return jsonify(m)


@app.route('/buy/<int:item_number>', methods=['GET'])
#The theory behind memoization is that if you have a function you need to call several times in one request .
#https://pythonhosted.org/Flask-Cache
def buy(item_number):
    #Round robin
    global currentOrderServer, flagsOrderServer
    chooseOrder=''
    if currentOrderServer == 0 and flagsOrderServer['order1'] == 1:
        chooseOrder='1'
        currentOrderServer = 1
        url = 'http://{}:{}/buy/{}'.format(orderIp, orderPort, item_number) 
    elif flagsOrderServer['order2']==1 :
        chooseOrder ='2'
        currentOrderServer = 0
        url = 'http://{}:{}/buy/{}'.format(orderIp2, orderPort2, item_number) 
    else :
        chooseOrder ='1'
        currentOrderServer = 1
        url = 'http://{}:{}/buy/{}'.format(orderIp, orderPort, item_number) 
 
    print("Client wants to buy book number {}".format(item_number))
    print("Sending buy request to the order {} server.".format(chooseOrder))
    n = requests.get(url)
    response = json.loads(n.text)
    return jsonify(response)
 

if __name__ == '__main__':
    app.run()
