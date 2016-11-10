# import from flask
from flask import Flask, render_template, redirect, url_for, request
# Import methods for tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# import es 
from elasticsearch import Elasticsearch, ElasticsearchException

# scoring tool
from textblob import TextBlob

import json
import logging
import os

app = Flask(__name__)

# config es
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

# tweet class with the relevant data that will be index to ES
class Tweet(object):
    def __init__(self, tweet_id, text, geo, score):
        self.tweet_id = str(tweet_id)
        self.text = text
        self.lat = geo[0]
        self.lon = geo[1]
        self.score = score

class StdOutListener(StreamListener):
    def on_data(self, data):
        # convert returned data to json
        json_data = json.loads(data)
        if 'geo' in json_data.keys():
            print json_data['geo']
        # store only data with geo point
        if 'geo' in json_data.keys() and json_data['geo']:
            # calculate the score of the tweet
            score = TextBlob(json_data['text']).sentiment.polarity
            # create object of tweet with the relevant data from the response
            tweet = Tweet(json_data['id'], json_data['text'], json_data['geo'][u'coordinates'], score)

            try:
                # index to es
                es.index(index="tweets", doc_type="tweet", id=tweet.tweet_id, body={"text": tweet.text,
                                                                                    "location": {"lat": tweet.lat, 
                                                                                                 "lon": tweet.lon
                                                                                                },
                                                                                    "score": tweet.score
                                                                                    })
            except ElasticsearchException:
                logging.exception('')
        return True

    def on_error(self, status):
        print "error", status

#handles Twitter authetification and the connection to Twitter Streaming API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, StdOutListener())
stream.filter(locations=[-180,-90,180,90])


# es query for tweets in specific location
def search_query(latitude, longitude, distance):
    return json.dumps({
            "size": 250,
            "sort" : [
                        { "score" : {"order" : "desc"}}
                    ],
            "query": 
                { "bool" : 
                    { "must" : 
                        {"match_all" : {}
                    }, "filter" : 
                        {"geo_distance" : 
                            {"distance" : 
                                "{distance}km".format(distance=distance), 
                                "location" : 
                                    "{latitude}, {longitude}"
                                    .format(latitude=latitude, 
                                        longitude=longitude)
                            }
                        }
                    }
                }
            })


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        latitude = request.form['lat']
        longitude = request.form['long']
        distance = request.form['distance']
        res = es.search(index="tweets", doc_type="tweet", body=search_query(latitude, longitude, distance))
        data = [data_point[u'_source'][u'text'] for data_point in res[u'hits'][u'hits']]
        print(data)
        return render_template('index.html', data=data)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  