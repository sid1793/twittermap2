#!/bin/env python
# encoding: utf-8

"""
Webservice prototype for exposing cell data via
HTTP and JSON/JSONP
"""


DB = 'tstream'
CELLS_COLLECTION = 'tweets'

import json
import time
import math
import redis
import threading
import signal
import sys
from flask import Flask
from flask import request
from flask import abort
from flask import url_for
from flask import make_response
from flask import Response
from pymongo import MongoClient
from pymongo import CursorType
from bson import json_util
from threading import Thread

i = 0
ci=0

red = redis.StrictRedis()

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)

def tail_mongo_thread(keyword):
    global ci
    print "beginning to tail..."
    db = MongoClient().tstream
    coll = db.tweets_tail
    cursor = coll.find({"coordinates.type" : "Point"}, cursor_type = CursorType.TAILABLE_AWAIT)
    while cursor.alive:
        try:
            doc = cursor.next()
            # print [k['text'] for k in doc['entities']['hashtags']]
            # time.sleep(3)
            if keyword != '':
                if any(keyword in k['text'] for k in doc['entities']['hashtags']):                  
                    ci += 1
                    print doc['entities']['hashtags']
                    # time.sleep(2)
                    red.publish('chat', u'%s' % json.dumps(doc, default=json_util.default))                  
            else:
                ci += 1
                red.publish('chat', u'%s' % json.dumps(doc, default=json_util.default))
                # print ci, " pub in redis"
        except StopIteration:
            pass

def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('chat')
    global i
    for message in pubsub.listen():
        i+=1
        print i, ' retrieved from redis'
        yield 'data: %s\n\n' % message['data']

    
app = Flask(__name__)

@app.route('/tweets')
def tweets():   
    url_for('static', filename='map.html')
    url_for('static', filename='jquery-1.7.2.min.js')
    url_for('static', filename='jquery.eventsource.js')
    url_for('static', filename='jquery-1.7.2.js')
    return Response(event_stream(), headers={'Content-Type':'text/event-stream'})
    
def runThread():
    # keyword = request.form.get('keyword', '')
    # print "In run: ", keyword
    st = Thread(target = tail_mongo_thread(''))
    st.start()




    

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    #app.before_first_request(runThread)
    app.run(debug=True, host='0.0.0.0')  



