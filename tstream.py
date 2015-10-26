import tweepy
import json
from pymongo import MongoClient
from bson import json_util
from tweepy.utils import import_simplejson


json = import_simplejson()
mongocon = MongoClient()

db = mongocon.tstream
col = db.tweets_tail

consumer_key = '###############'
consumer_secret = '################'

access_token_key = '###################'
access_token_secret = '#####################'

auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)
k = 0

class StreamListener(tweepy.StreamListener):
    mongocon = MongoClient()
    db = mongocon.tstream
    col = db.tweets_tail
    json = import_simplejson()

    def on_status(self, tweet):
        print 'Ran on_status'

    def on_error(self, status_code):
        return False

    def on_data(self, data): 
        global k      
        if data[0].isdigit():
            pass
        else:
            k += 1
            col.insert(json.loads(data))
            print(k)


l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l)
# setTerms = ['bonjour', 'chaussette']
# streamer.filter(track = setTerms, locations=[-180,-90,180,90])
streamer.filter(locations=[-180,-90,180,90])
#If you want no filter pass: locations=[-180,-90,180,90]
