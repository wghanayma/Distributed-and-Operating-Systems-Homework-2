from flask import Flask, jsonify
import requests
import json
import datetime
import socket
import os
import csv
app = Flask("order Server")
# IP address and port number of catalog server.
catalog_ip = "192.168.1.210"
catalog_port = 5000


def create_data_file():
    file_exists = os.path.isfile(os.getcwd() + '/order_logs.csv')
    if file_exists is False:
        with open(file_exists, 'w', newline='') as file:
            thewriter = csv.writer(file)
            thewriter.writerow(
                ['Item Number', 'Status', 'Date', 'Remaining Stock'])


@app.route('/buy/<int:item_number>', methods=['GET'])
def buy_request(item_number):
    # Queries the catalog server to check if the stock is not empty
    check_buy_book = requests.get(
        'http://{}:{}/query_by_item/{}'.format(catalog_ip, catalog_port, item_number))
    current_name = check_buy_book.json()['title']
    current_stock = check_buy_book.json()['stock']
    print("Received buy request : Name : {} ,Stock : {} .".format(
        current_name, current_stock))
    if current_stock > 0:
        n = requests.get(
            'http://{}:{}/update/{}/decrease_stack/1'.format(catalog_ip, catalog_port, item_number))
        with open('order_logs.csv', 'a') as file:
            thewriter = csv.writer(file)
            thewriter.writerow([item_number,  'Order Completed',
                                datetime.datetime.now(),
                                str(current_stock - 1)])
        print("Order Completed : Name :{} ,Stock : {}".format(
            current_name, current_stock-1))
        return jsonify("Transaction successful.")
    else:
        return jsonify("Oops! We ran out of {}'s stock. Please try again after sometime.".format(item_number))
@app.route('/')
def main():
    return "order Server"

if __name__ == '__main__':
    create_data_file()
    app.run()
