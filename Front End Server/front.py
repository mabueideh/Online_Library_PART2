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


#THIS IS FOR IMPLEMENTING THE CACHE
cache = {} 
lru = {}

def add_request(key,value):     #adds entry to cache   
    cache[key] = value
    lru[key] = 0
    return

def delete_request(key):        #deletes entry from cache
    if key in cache:
        del cache[key]
        del lru[key]
    return

def increment_lru():            #increment the value of entries in the lru dictionary
    for key in lru:    
        lru[key] +=  1
    return

def maximum_key():              #return the key with maximum lru value
    return max(lru, key=lambda k: lru[k])

def update_lru(key):            #resets the lru value of a key to zero
    lru[key] = 0
    return

def cache_full():               #checks if the cache is full
    cache_size = 4
    if(len(cache.keys()) >= cache_size):
        return True
    else:
        return False
#CACHE IMPLEMTING ENDS HERE



@front.route('/search/<topic>' ,methods=['POST','GET']) #received search request
def search(topic):
    global cat_id
    increment_lru() #incrementing values in the lru dictionary
    key_request = 'search/' + topic #generating a key
    if(key_request in cache):       #cache hit
        update_lru(key_request)     #update the lru to be 0    
        return cache[key_request]   #return response to client
    else:                           #cache miss
        if(cat_id == 0):    #checks if it's the first catalog server turn in load balancing
            cat_id = 1
            request = 'http://' + Cat_IP1 + '/search/' + topic
        else:                       
            cat_id = 0
            request = 'http://' + Cat_IP2 + '/search/' + topic

        response = requests.get(request).content    #get response from catalog server

        request_value = jsonify(json.loads(response))   #generating the value

        if(cache_full()):
            max_lru = maximum_key() #find the key with the max value, longest time in the cache
            delete_request(max_lru) #delete that entry

        add_request(key_request,request_value) #add the new entry to the cache

        return jsonify(json.loads(response))            #return response to client


@front.route('/lookup/<id>' ,methods=['POST','GET']) #received lookup request
def lookup(id):
    global cat_id
    increment_lru() #incrementing values in the lru dictionary
    key_request = 'lookup/' + id    #generating a key
    if(key_request in cache):       #cache hit
        update_lru(key_request)     #update the lru to be 0   
        return cache[key_request]   #return response to client
    
    else:                           #cache miss
        if(cat_id == 0):    #checks if it's the first catalog server turn in load balancing
            request = 'http://' + Cat_IP1 + '/lookup/' + id
            cat_id = 1
        else:
            request = 'http://' + Cat_IP2 + '/lookup/' + id
            cat_id = 0
    
        response = requests.get(request) #get response from catalog server
        
        request_value = response.json()  #generating the value

        if(cache_full()):
            max_lru = maximum_key() #find the key with the max value, longest time in the cache
            delete_request(max_lru) #delete that entry

        add_request(key_request,request_value)  #add the new entry to the cache


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


@front.route('/invalidate/<id>' ,methods=['POST','GET']) #received invalidate request
def remove_cache(id):
    key_request = 'lookup/' + id #generate key of the entry
    delete_request(key_request) #remove specified id from in memory cache
    return "dummy value"
    



if __name__ == "__main__":
    front.run(host= Front_IP)
    #front.run(host= Front_IP, port=8000)
    front.run(debug=True)
