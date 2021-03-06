from flask import Flask, jsonify
import os
import sqlite3
import json
import socket
import time
import requests
import ast

app = Flask("Catalog Server")
#Update (URLs)
@app.route('/')
def main():
    return "Catalog Server"



# IP address and port number of Catalog 2 server.
catalogIp2 = "192.168.1.123"
catalogPort2 = 5000

# IP address and port number of FrontEnd server.
frontEndIp = "192.168.1.208"
frontEndPort = 5000
# Create a database and create a table
# Database storage location
# /home/osboxes/Distributed-and-Operating-Systems-Homework-1/catalog/catalogdatabase.db
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), __name__+'Database.db')


def create_database():
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    # Create a database if not exists.
    books_sql = """
        CREATE TABLE IF NOT EXISTS books (
		         id INTEGER PRIMARY KEY AUTOINCREMENT,
	             number_of_items INTEGER NOT NULL,
	             title TEXT(200) NOT NULL,
                 topic TEXT(200) NOT NULL,
	             cost  INTEGER NOT NULL,
	             stock INTEGER NOT NULL
                                          )"""
    cursor.execute(books_sql)
    # Commit the changes to database
    connection.commit()
    # Close the connection
    cursor.close()

    # Bring all the books from the database with details .


def books_from_database():
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    sql_query = "SELECT * FROM books"
    cursor.execute(sql_query)
    # returns a books from database to list
    all_books = cursor.fetchall()
    cursor.close()
    return all_books


def insert_list_of_books_in_database():
    available_books_in_a_stock = [
        # (number of item, topic of the book, title of item , cost, stock)
        (1, 'How to get a good grade in DOS in 20 minutes a day','distributed_systems', 10, 1000),
        (2, 'RPCs for Dummies', 'distributed_systems', 10, 1000),
        (3, 'Xen and the Art of Surviving Graduate School','graduate_school', 10, 1000),
        (4, 'Cooking for the Impatient Graduate Student', 'graduate_school', 10, 1000),
        (5, 'How to finish Project 3 on time','graduate_school', 10, 1000),
        (6, 'Why theory classes are so hard.','graduate_school', 10, 1000),
        (7, 'Spring in the Pioneer Valley','graduate_school', 10, 1000)
                                ]
    # if the database doesn't contain all the 4 books, then insert them into the database
    if len(books_from_database()) < 7:
        # Connect to a SQLite database by specifying the database file name
        connection = sqlite3.connect(DEFAULT_PATH)
        cursor = connection.cursor()
        # Insert multiple books in a single query
        insertStatement = "INSERT INTO books VALUES (NULL,?,?,?,?,?)"
        cursor.executemany(insertStatement, available_books_in_a_stock)
        # Commit the changes to database
        connection.commit()
        # Close the connection
        cursor.close()

# create database and insert the books


create_database()
insert_list_of_books_in_database()

# Query

# Query database by topics :
# 1- distributed_systems
# 2- graduate_school


def query_by_topic(topic_string):
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    sql_query = "SELECT * FROM books WHERE topic=?"
    cursor.execute(sql_query, [(topic_string)])
    book_list_topic = cursor.fetchall()
    # Close the connection
    cursor.close()
    return book_list_topic

# Query database by number of item


def query_by_book_number(number_of_items):
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    sql_query = "SELECT * FROM books WHERE number_of_items=?"
    cursor.execute(sql_query, [(number_of_items)])
    single_book = cursor.fetchone()
    # Close the connection
    cursor.close()
    return single_book

# Update

# Update the number of copies available for the book in stock.

def update_book_stock(number_of_items, new_stock_count):
    send_data_from_catalog_to_catlog_2("update_book_stock",number_of_items,new_stock_count)
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    cursor.execute('''UPDATE books SET stock = ? WHERE number_of_items = ? ''',
                   (new_stock_count, number_of_items))
    # Commit the changes to database
    connection.commit()
    # Close the connection
    cursor.close()

#  Update the number of copies available for the book in stock from Replica 
def update_book_stock_replica(item,dataFromCatalog2):
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    cursor.execute('''UPDATE books SET stock = ? WHERE number_of_items = ? ''',
                (dataFromCatalog2, item))
    #Commit the changes to database
    connection.commit()
        # Close the connection
    cursor.close()

# Update the cost of a specific book in stock.

def update_book_cost(number_of_items, new_book_cost):
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    cursor.execute('''UPDATE books SET cost = ? WHERE number_of_items = ? ''',
                   (new_book_cost, number_of_items))
    # Commit the changes to database
    connection.commit()
    # Close the connection
    cursor.close()
    send_data_from_catalog_to_catlog_2("update_book_cost",number_of_items,new_book_cost)

# Update the cost of a specific book in stock from Replica.
def update_book_cost_replica(item,dataFromCatalog2):
    # Connect to a SQLite database by specifying the database file name
    connection = sqlite3.connect(DEFAULT_PATH)
    cursor = connection.cursor()
    cursor.execute('''UPDATE books SET cost = ? WHERE number_of_items = ? ''',
                   (dataFromCatalog2, item))
        # Commit the changes to database
    connection.commit()
        # Close the connection
    cursor.close()
        

# send data to catalog 2 
def send_data_from_catalog_to_catlog_2(operation,item,dataSend):
    if operation == "update_book_stock":
        response = requests.get(
                'http://{}:{}/update_replicas/{}/{}/{}'.format(catalogIp2, catalogPort2, operation,item,dataSend))
    elif operation == "update_book_cost":
        response = requests.get(
                'http://{}:{}/update_replicas/{}/{}'.format(catalogIp2, catalogPort2, operation,item,dataSend))
    else:
        print("No operation specified !")

@app.route('/update_replicas/<operation>/<int:item>/<int:data>', methods=['GET'])
def receive_from_catlog_2_data(operation,item, data):
    if operation == "update_book_stock":
        update_book_stock_replica(item,data)
    elif operation == "update_book_cost":
        update_book_cost_replica(item,data)
    else:
        print("No operation specified !")


    return jsonify("confirmed: received Catalog 2 data")



@app.route('/update/<int:book_number>/<operation>/<int:change>', methods=['GET'])
def update(book_number, operation, change):
    book = query_by_book_number(book_number)
    if operation == 'decrease_stack':
        if query_by_book_number(book_number)[5] >= 1:
            m = requests.get('http://{}:{}/invalidate/{}'.format(frontEndIp, frontEndPort, book_number))
            new_stock = book[5] - change
            print("Received update request from order server for book {} and the new stock is {}.".format(
            book_number, new_stock))
            update_book_stock(book_number, new_stock)
            return jsonify({'new_stock': new_stock})
    if operation == 'increase_stack':
            m = requests.get('http://{}:{}/cache/invalidate/{}'.format(frontEndIp, frontEndPort, book_number))
            new_stock = book[5] + change
            update_book_stock(book_number, new_stock)
            print("Received update request from order server for book {} and new stock is {} .".format(
            book_number, new_stock))
            return jsonify({'new_stock': new_stock})
    if operation == 'update_cost':
            m = requests.get('http://{}:{}/cache/invalidate/{}'.format(frontEndIp, frontEndPort, book_number))
            new_book_cost = change
            update_book_cost(book_number, new_book_cost)
            print("Received update request from order server for book {} and a new cost is {} .".format(
            book_number, new_book_cost))
            return jsonify({'new_cost': new_book_cost})

# Query by subject (URLs)
# 1- distributed_systems
# 2- graduate_school
@app.route('/query_by_subject/<book_topic>', methods=['GET'])
def query_by_subject(book_topic):
    books = query_by_topic(book_topic)
    if len(books) == 0:
        return jsonify("There is no relevant book available associated with topic- {}".format(book_topic))
    
    books_dict = {}
    for book_row in books:
        books_dict[book_row[3]] = book_row[1]
    return jsonify({'items': books_dict})

# Query by item (URLs)
@app.route('/query_by_item/<int:book_number>', methods=['GET'])
def query_by_item(book_number):
    book = query_by_book_number(book_number)
    print("Query by item : Book Number :{} ,Name :{} ,Stock : {} Cost: ${},".format(
        book_number, book[2], book[5], book[4]))

    if book is None:
        return jsonify("There is no book available of number {} has name :{}".format(book_number, book[2]))
    book_dict = {
        "number_of_items": book[1], "title": book[2], "stock": book[5], "cost": book[4]}
    return jsonify(book_dict)


if __name__ == '__main__':

    app.run()
