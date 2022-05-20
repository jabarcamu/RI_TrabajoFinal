import json
import tweepy
from tweepy import OAuthHandler

# Authenticate
CONSUMER_KEY = "UH4N5hOhJFbJBdOJwTnTzqFsg" #@param {type:"string"}
CONSUMER_SECRET_KEY = "1k4OMxuGAMOYWYRfHHTPyQeRb54sPLTn3pC62XrpGZzgOfsBW3" #@param {type:"string"}
ACCESS_TOKEN_KEY = "1441326109-HCOavAblDFkF2cWmjEREWKu2bLhmK7pxrRW4Ry7" #@param {type:"string"}
ACCESS_TOKEN_SECRET_KEY = "YEXDEcYt6XieRMVpOeb8Y4g2ClhtAKqnFSRSbqAkj0h9v" #@param {type:"string"}

#Creates a JSON files with api credentials
with open("api_keys.json", "w") as outfile:
    json.dump({
        "consumer_key": CONSUMER_KEY,
        "consumer_secret": CONSUMER_SECRET_KEY,
        "access_token": ACCESS_TOKEN_KEY,
        "access_token_secret": ACCESS_TOKEN_SECRET_KEY
    }, outfile)


