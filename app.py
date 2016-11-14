# import from flask
from flask import Flask, render_template, redirect, url_for, request
# Import methods for tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# import es
from elasticsearch import Elasticsearch, ElasticsearchException, helpers
import certifi
from es_queries import search_query

from textblob import TextBlob
# google map
from flask_googlemaps import GoogleMaps, Map
from google_map_functions import marked_map

import json
import logging
import os
import threading

app = Flask(__name__)

# config es
es = Elasticsearch([{'host': 'f840a143ab945c2b14a9abf4bc0764c9.us-east-1.aws.found.io', 'port': 9243}],
    http_auth=(os.environ['ES_USERNAME'],os.environ['ES_PASSWORD']), use_ssl=True)

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

GoogleMaps(app, key=os.environ['GOOGLEMAPS_KEY'])

# tweet class with the relevant data that will be index to ES
class Tweet(object):
    def __init__(self, tweet_id, text, geo, score):
        self.tweet_id = str(tweet_id)
        self.text = text
        self.lat = geo[0]
        self.lon = geo[1]
        self.score = score

# handele the twitter streaming
class StdOutListener(StreamListener):
    def __init__(self):
        self.tweets_list = []
    def on_data(self, data):
        # convert returned data to json
        json_data = json.loads(data)
        # store only data with geo point
        if 'geo' in json_data.keys() and json_data['geo']:
            # calculate the score of the tweet
            score = TextBlob(json_data['text']).sentiment.polarity
            # create object of tweet with the relevant data from the response
            tweet = Tweet(json_data['id'], json_data['text'], json_data['geo'][u'coordinates'], score)
            # append tweet to a list that in the future will save as bulk 
            self.tweets_list.append({
                    "_index": "tweets",
                    "_type": "tweet",
                    "_id": tweet.tweet_id,
                    "_source": {
                        "text": tweet.text,
                        "location": {"lat": tweet.lat, 
                        "lon": tweet.lon
                        },
                        "score": tweet.score
                    }
                })
            try:
                # index bulk to reduce calls to es
                if len(self.tweets_list) > 1000:
                    helpers.bulk(es, self.tweets_list)
                    self.tweets_list =[]
            except ElasticsearchException:
                logging.exception('')
        return True

    def on_error(self, status):
        print "error", status

#handles Twitter authetification and the connection to Twitter Streaming API
def twitter():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, StdOutListener())
    stream.filter(locations=[-180,-90,180,90])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
            latitude = request.form['lat']
            longitude = request.form['long']
            distance = request.form['distance']
            search_key = request.form['search_key']
            if -90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180  and distance > 0:
                res = es.search(index="tweets", doc_type="tweet", body=search_query(latitude, longitude, distance, search_key))
                data = [data_point[u'_source'] for data_point in res[u'hits'][u'hits']]
                return render_template('index.html', data=data, message='success', sndmap=marked_map(data, latitude, longitude))
            else:
                return render_template('index.html', message='invalid values', sndmap='')
    return render_template('index.html', sndmap='')

# threading for the twitter + start 
twitter_stream = threading.Thread(name='twitter_function', target=twitter)
twitter_stream.setDaemon(True)
twitter_stream.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
