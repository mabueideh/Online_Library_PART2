from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import requests
import urllib.parse

catalog = Flask(__name__)

catalog.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Books.db'

db = SQLAlchemy(catalog)

ma = Marshmallow(catalog)

#CREATING THE DATABASE
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    
class BookSchema_search(ma.Schema):
    class Meta:
        fields = ('id','topic','name')
books_schema_search = BookSchema_search(many = True)

class BookSchema_lookup(ma.Schema):
    class Meta:
        fields = ('id','quantity','price')
book_schema_lookup = BookSchema_lookup()

#END OFCREATING THE DATABASE

Cat_IP = '192.168.1.114'            #second catalog server(host)
Cat_IP2 = '192.168.1.108:5000'      #first catalog server
Front_IP = '192.168.1.107:5000'     #front-end server(host)


@catalog.route('/search/<subject>' ,methods=['POST','GET']) #received search request
def search(subject):
    urllib.parse.unquote(subject)                       #enscape request, return the request as it was (with spaces instead of %20)
    all_books = Book.query.filter(Book.topic== subject) #create a querry get books that has the desired topic
    result = books_schema_search.dump(all_books)        #get books that has the desired topic
    return jsonify(result)                              #return books in a json format to front-end server


@catalog.route('/lookup/<id>' ,methods=['POST','GET']) #received lookup request
def lookup(id):
    my_book = Book.query.get(id)                #create a querry get book that has the desired id
    return book_schema_lookup.jsonify(my_book)  #get book that has the desired id and return it to front-end server

@catalog.route('/quantity/<id>' ,methods=['POST','GET']) #received quantity request
def get_quantity(id):
    my_book = Book.query.get(id)    #create a querry get book that has the desired id
    return str(my_book.quantity)    #get quantity of book that has the desired id and return it to front-end server


@catalog.route('/update/<id>' ,methods=['POST','GET']) #received update request
def decrement(id):
    my_book = Book.query.get(id)        #create a querry get book that has the desired id
    book_quantity = my_book.quantity-1
    my_book.quantity = book_quantity
    db.session.commit()         #make changes to database
    request = 'http://' + Cat_IP2 + '/modify/' + id + '/' + str(book_quantity)    
    dummy = requests.get(request).content #send a request to catalog server to modify value, for consistency

    request = 'http://' + Front_IP + '/invalidate/' + id     
    dummy = requests.get(request).content #send a request to front-end server to delet entry, for cache consistency
    return str("dummy_value")


@catalog.route('/modify/<id>/<value>' ,methods=['POST','GET']) #received modify request
def keep_consistent(id,value):
    my_book = Book.query.get(id)        #create a querry get book that has the desired id
    my_book.quantity = int(value)       #get new quantity value
    db.session.commit()         #make changes to database
    return str("dummy value")


if __name__ == "__main__":
    catalog.run(host= Cat_IP)
    catalog.run(debug=True)
