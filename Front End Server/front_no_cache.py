from flask import Flask , request , jsonify
from flask_marshmallow import Marshmallow
import requests
import json

front = Flask(__name__)

Order_IP1 = '192.168.1.109:5000'    #first order server
Order_IP2 = '192.168.1.115:5000'    #second order server
Front_IP = '192.168.1.107'          #front-end server(host)
Cat_IP1 = '192.168.1.108:5000'      #first catalog server
Cat_IP2 = '192.168.1.114:5000'      #second catalog server

order_id = 0    #order server id
cat_id = 0      #catalog server id


@front.route('/search/<topic>' ,methods=['POST','GET']) #received search request
def search(topic):
    global cat_id
    if(cat_id == 0):    #checks if it's the first catalog server turn in load balancing
        cat_id = 1
        request = 'http://' + Cat_IP1 + '/search/' + topic
    else:                       
        cat_id = 0
        request = 'http://' + Cat_IP2 + '/search/' + topic

    response = requests.get(request).content    #get response from catalog server

    return jsonify(json.loads(response))            #return response to client


@front.route('/lookup/<id>' ,methods=['POST','GET']) #received lookup request
def lookup(id):
    global cat_id
    if(cat_id == 0):    #checks if it's the first catalog server turn in load balancing
        request = 'http://' + Cat_IP1 + '/lookup/' + id
        cat_id = 1
    else:
        request = 'http://' + Cat_IP2 + '/lookup/' + id
        cat_id = 0
            
    response = requests.get(request) #get response from catalog server
                
    return response.json()  #return response to client


@front.route('/buy/<id>' ,methods=['POST','GET']) #received buy request
def get_quantity(id):
    global order_id
    if(order_id == 0):  #checks if it's the first order server turn in load balancing
        request = 'http://' + Order_IP1 + '/buy/' + id
        order_id = 1
    else:
        request = 'http://' + Order_IP2 + '/buy/' + id
        order_id = 0

    return requests.get(request).content #return response to client

if __name__ == "__main__":
    front.run(host= Front_IP)
    #front.run(host= Front_IP, port=8000)
    front.run(debug=True)
