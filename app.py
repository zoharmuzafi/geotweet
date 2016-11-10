# import from flask
from flask import Flask, render_template, redirect, url_for
# Import methods for tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import os

app = Flask(__name__)

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

class StdOutListener(StreamListener):
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print "error", status


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    #This handles Twitter authetification and the connection to Twitter Streaming API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, StdOutListener())
    stream.filter(locations=[-122.75,36.8,-121.75,37.8,-74,40,-73,41])
