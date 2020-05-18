from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
import requests

order = Flask(__name__)


Order_IP = '192.168.1.115'          #second order server(host)
Cat_IP = '192.168.1.114:5000'       #second catalog server

@order.route('/buy/<id>' ,methods=['POST','GET'])   #received buy request
def get_quantity(id):
    request = 'http://' + Cat_IP + '/quantity/' + id        #generating the quantity request
    quantity = int(requests.get(request).content)           #sending a request to catalog to server to know the quantity of the book
    if quantity > 0:                                        #chacks if the ammount if sufficient
        request = 'http://' + Cat_IP + '/update/' + id      #generating the update request
        requests.get(request)                               #sending the request the catalog server
        return 'The book has been purchased successfully'   #return response to front-end server
    else:
        return 'This book is out of stock'                  #return response to front-end server



if __name__ == "__main__":
    order.run(host = Order_IP)
    order.run(debug=True)
