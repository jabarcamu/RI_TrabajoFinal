import random

no_samples = "1000"
list_tweets = None

with open("hydrated_tweets_short.json","r") as myfile:
    list_tweets = list(myfile)

if int(no_samples) > len(list_tweets):
    no_samples = len(list_tweets)

sample = random.sample(list_tweets, int(no_samples))

file = open("sample_data.json", "w")
for i in sample:
    file.write(i)
file.close()
