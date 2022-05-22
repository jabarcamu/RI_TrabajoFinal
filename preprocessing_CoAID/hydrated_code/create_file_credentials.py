import json
import tweepy
from tweepy import OAuthHandler

# Authenticate
CONSUMER_KEY = "" #inserta consumer_key de twitter dev
CONSUMER_SECRET_KEY = "" #inserta consumer_secret_key de twitter dev
ACCESS_TOKEN_KEY = "" #inserta access_token_key de twitter dev
ACCESS_TOKEN_SECRET_KEY = "" #@inserta access_token_secret_key de twitter dev

#Creates a JSON files with api credentials
with open("api_keys.json", "w") as outfile:
    json.dump({
        "consumer_key": CONSUMER_KEY,
        "consumer_secret": CONSUMER_SECRET_KEY,
        "access_token": ACCESS_TOKEN_KEY,
        "access_token_secret": ACCESS_TOKEN_SECRET_KEY
    }, outfile)


