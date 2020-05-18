from flask import Flask, jsonify
import time
import requests
import json
import csv
import random

app = Flask(__name__)
#CACHE_TYPE is simple which means that Will use in memory pickle and is recommended only for single process development server .
#http://brunorocha.org/python/flask/using-flask-cache.html
SizeCache=0
# IP address and port number of Catalog 1 server.
catalogIp = "192.168.1.210"
catalogPort = 5000
# IP address and port number of Catalog 2 server.
catalogIp2 = "192.168.1.123"
catalogPort2 = 5000
# IP address and port number of Order 1 server.
orderIp = "192.168.1.222"
orderPort = 5000
# IP address and port number of Order 2 server.
orderIp2 = "192.168.1.149"
orderPort2 = 5000

# IP address and port number of FrontEnd server.
frontEndIp = "192.168.1.208"
frontEndPort = 5000
url = 'http://{}:{}/'.format(frontEndIp, frontEndPort) 

cached_data = dict()

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
#@cache.memoize(timeout = 30)
def lookupRequest(item_number):
    print(cached_data)
    try:
        start = time.time()
        m = cached_data[item_number]
        end = time.time()
        time_taken = (end - start)
        print "%.2gs" % (time_taken)
        return jsonify(m)
    except:
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
        start = time.time()
        m = requests.get(url)
        print("Lookup : Name : {} ,Stock : {} ,Cost :{}$".format(
        m.json()['title'], m.json()['stock'], m.json()['cost']))
        data_to_cache = { 'cost':m.json()['cost'],'number_of_items':m.json()['number_of_items'], 'stock':m.json()['stock'],'title':m.json()['title']}
        if len(cached_data)>SizeCache and len(cached_data)!=0:
            print("Remove Last Item from Cache.")
            cached_data.popitem()
        elif len(cached_data)<=SizeCache and SizeCache :
            cached_data[item_number] = data_to_cache
        else:
            print("No Cache.")
        m = json.loads(m.text)
        end = time.time()
        time_taken = (end - start)
        #string_time_taken = "{:.2f}".format(time_taken)
        print "%.2gs" % (time_taken)
        #print("Lookup took {} seconds".format(string_time_taken))
        print("Forwarding query results to the client.")
        return jsonify(m)

@app.route("/invalidate/<int:item_number>")
def invalidate(item_number):
    print("Size cache :{}".format(len(cached_data)))
    print("Invalidating cache data for item number :{}".format(item_number))
    cached_data.pop(item_number, None)
    return jsonify({'invalidated' : True})

@app.route('/test_cached/<int:numbersTest>/sizeCached/<int:sizeCached>')
def test(numbersTest,sizeCached):
    global SizeCache
    SizeCache=sizeCached
    time_taken_cached = 0.0
    time_taken_uncached = 0.0
    for i in range(numbersTest):
		start_time = time.time()
		r = requests.get(url + 'lookup/{}'.format(random.randint(1,7)))
		end_time1 = time.time()
		r = requests.get(url + 'lookup/{}'.format(random.randint(1,7)))
		end_time2 = time.time()
		r = requests.get(url + 'buy/{}'.format(random.randint(1,7)))

		time_taken_cached += end_time2 - end_time1
		time_taken_uncached += end_time1 - start_time
    time_taken_uncached /= numbersTest
    time_taken_cached /= numbersTest
    cached_data.clear()
    print("Average time per cached search after doing {} sequential buys is :{} seconds\n" .format(numbersTest,time_taken_cached))
    print("Average time per uncached search after doing {} sequential buys is :{} seconds\n".format(numbersTest,time_taken_uncached))
    
    return jsonify({'numbersTest': numbersTest,'average_time_taken_uncached': time_taken_uncached,'average_time_taken_cached': time_taken_cached})

@app.route('/test_uncached/<int:numbersTest>/sizeCached/<int:sizeCached>')
def testUncached(numbersTest,sizeCached):
    global SizeCache
    SizeCache=sizeCached
    time_taken_cached = 0.0
    time_taken_uncached = 0.0
    for i in range(numbersTest):
		start_time = time.time()
		r = requests.get(url + 'lookup/{}'.format(1))
		end_time1 = time.time()
		r = requests.get(url + 'lookup/{}'.format(1))
		end_time2 = time.time()
		r = requests.get(url + 'buy/{}'.format(1))

		time_taken_cached += end_time2 - end_time1
		time_taken_uncached += end_time1 - start_time
    time_taken_uncached /= numbersTest
    time_taken_cached /= numbersTest
    cached_data.clear()
    print("Average time per cached search after doing {} sequential buys is :{} seconds\n" .format(numbersTest,time_taken_cached))
    print("Average time per uncached search after doing {} sequential buys is :{} seconds\n".format(numbersTest,time_taken_uncached))
    return jsonify({'numbersTest': numbersTest,'average_time_taken_uncached': time_taken_uncached,'average_time_taken_cached': time_taken_cached})

@app.route('/test_lookup/<int:numbersTest>/sizeCached/<int:sizeCached>')
def testLookup(numbersTest,sizeCached):
    global SizeCache
    SizeCache=sizeCached
    time_taken = 0.0
    for i in range(numbersTest):
		start_time = time.time()
		r = requests.get(url + 'lookup/{}'.format(random.randint(1,7)))
		end_time = time.time()
		time_taken += end_time - start_time
    time_taken /= numbersTest
    cached_data.clear()
    print("Average time loopup after doing {} sequential buys is :{} seconds\n" .format(numbersTest,time_taken))
    return jsonify({'numbersTest': numbersTest,'average_time_taken': time_taken})
@app.route('/test_search/<int:numbersTest>/sizeCached/<int:sizeCached>')
def testSearch(numbersTest,sizeCached):
    global SizeCache
    SizeCache=sizeCached
    time_taken = 0.0
    for i in range(numbersTest):
		start_time = time.time()
		r = requests.get(url + 'search/{}'.format (random.choice(['distributed_systems', 'graduate_school'])))
		end_time = time.time()
		time_taken += end_time - start_time
    time_taken /= numbersTest
    cached_data.clear()
    print("Average time search after doing {} sequential buys is :{} seconds\n" .format(numbersTest,time_taken))
    return jsonify({'numbersTest': numbersTest,'average_time_taken': time_taken})
@app.route('/test_buy/<int:numbersTest>/sizeCached/<int:sizeCached>')
def testBuy(numbersTest,sizeCached):
    global SizeCache
    SizeCache=sizeCached
    time_taken = 0.0
    for i in range(numbersTest):
		start_time = time.time()
		r = requests.get(url + 'buy/{}'.format (random.randint(1,7)))
		end_time = time.time()
		time_taken += end_time - start_time
    time_taken /= numbersTest
    cached_data.clear()
    print("Average time search after doing {} sequential buys is :{} seconds\n" .format(numbersTest,time_taken))
    return jsonify({'numbersTest': numbersTest,'average_time_taken': time_taken})
@app.route('/buy/<int:item_number>', methods=['GET'])
#@cache.memoize(timeout = 30)
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
    start = time.time()
    n = requests.get(url,timeout = 5)
    response = json.loads(n.text)
    end = time.time()
    time_taken = (end - start)
    print "%.2gs" % (time_taken)
	#print("Buy took {} seconds\n".format(time_taken),' seconds)

    return jsonify(response)
 

if __name__ == '__main__':
    app.run()
