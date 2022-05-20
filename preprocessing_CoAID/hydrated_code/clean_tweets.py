#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   /$$$$$$  /$$      /$$ /$$      /$$ /$$$$$$$$
#  /$$__  $$| $$$    /$$$| $$$    /$$$|__  $$__/
# | $$  \__/| $$$$  /$$$$| $$$$  /$$$$   | $$   
# |  $$$$$$ | $$ $$/$$ $$| $$ $$/$$ $$   | $$   
#  \____  $$| $$  $$$| $$| $$  $$$| $$   | $$   
#  /$$  \ $$| $$\  $ | $$| $$\  $ | $$   | $$   
# |  $$$$$$/| $$ \/  | $$| $$ \/  | $$   | $$   
#  \______/ |__/     |__/|__/     |__/   |__/  
#
#
# Developed during Biomedical Hackathon 6 - http://blah6.linkedannotation.org/
# Authors: Ramya Tekumalla, Javad Asl, Juan M. Banda
# Contributors: Kevin B. Cohen, Joanthan Lucero

import pandas as pd
import numpy as np
import json
import sys
import string
import re
# This will load the fields list
import fields
from emot.emo_unicode import UNICODE_EMOJI, EMOJI_UNICODE
import emoji
import nltk
from wordcloud import STOPWORDS
import spacy
nlp = spacy.load("en_core_web_sm")

fieldsFilter = fields.fields

fileN = sys.argv[1]
preprocess = sys.argv[2]

data = []

tweet_df = pd.read_csv(fileN)
#with open(fileN, 'r') as f:
#    for line in f:
#        data.append(json.loads(line))


def remove_emoticons(text):
    emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in EMOJI_UNICODE) + u')')
    return emoticon_pattern.sub(r'', text)

def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_weird_urls(text):
    result = re.sub(r"\v\S*\\\S+","",text)
    return(result)

def remove_users(text):
    #remover usuarios
    result = re.sub(r"\@[A-Za-z0-9_]+", "", text)
    return(result)

def remove_onechar(text):
    result = re.sub(r"\b\w\b"," ",text)
    result = re.sub(r"\s{2,}", " ",result)
    return(result)

def remove_numbers(text):
    result = re.sub(r"[0-9]+",' ',text)
    return(result)

def remove_hashtags(text):
    result = re.sub(r"\#\S+",' ',text)
    return(result)

def remove_manyspaces(text):
    result = re.sub(r" +", " ",text)
    return(result)

def remove_urls(text):
    result = re.sub(r"\S*https?\S+", "", text) 
    return(result)

def remove_amps(text):
    result = re.sub(r"\S*amp?\S+","", text)
    return(result)

def remove_twitter_urls(text):
    clean = re.sub(r"pic.twitter\S+", "",text)
    return(clean)

def give_emoji_free_text(text):
    return emoji.get_emoji_regexp().sub(r'', text)
    #return emoji.replace_emoji(str, replace="")


def only_words(text):
    rx = re.compile(r"(\w+)")
    words = [m.group(0) for string in text.split() for m in [rx.search(string)] if m]
    result = " ".join(words)
    return(result)

def remove_weird_words(text):
    words = [kw for kw in text.split() if len(kw)>2]
    result = " ".join(words)
    return(result)

#definir stopwords y punctuations
"""
In order to make the graphs more useful we decided to prevent some words from being included
"""
ADDITIONAL_STOPWORDS = [
    "COVID",
    "COVID-19",
    "coronavirus",
    "covid"
]
for stopword in ADDITIONAL_STOPWORDS:
    STOPWORDS.add(stopword)

def cleanup_text(doc):
    punctuations = string.punctuation
    stop_words = list(STOPWORDS)
    doc = nlp(doc, disable=["parser","ner"])
    tokens = [tok.lemma_.lower().strip() for tok in doc if tok.lemma_ != "-PRON-"]
    tokens = [tok for tok in tokens if tok not in stop_words and tok not in punctuations]
    return " ".join(tokens)

#tweet_df = pd.json_normalize(data)
# Cleaner solution in case some of the fields in the list are non existent and/or have typos
tweet_df = tweet_df.loc[:, tweet_df.columns.isin(fieldsFilter)]

#Filtrar Tweets de lenguage english
tweet_df = tweet_df[tweet_df.lang=="en"]

tweet_df['text'] = tweet_df['text'].str.replace('\n','')
tweet_df['text'] = tweet_df['text'].str.replace('\r','')

if preprocess == 'p':

    print("removing_weird_urls")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_weird_urls(x))
    print("removing_amps")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_amps(x))
    print("removing_user_mentions")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_users(x))
    print("removing_standard_urls")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_urls(x))
    print("removing_hashtags")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_hashtags(x))
    print("removing_twitter_urls")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_twitter_urls(x))
    print("removing_emoticons")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_emoticons(x))
    print("removing_emoji")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_emoji(x))
    print("give_emoji_free_text")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : give_emoji_free_text(x))
    
    print("keeping only words")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : only_words(x))
    
    print("lemmatizatoin_and_removing_stopwords_punctuations")
    #remove stopwords punctuations and lemmatization
    tweet_df['text'] = tweet_df['text'].apply(lambda x : cleanup_text(x))
    
    print("removing_numbers")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_numbers(x))
    print("removing_manyspaces")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_manyspaces(x))
    print("removing_words_lessthanlen2")
    tweet_df['text'] = tweet_df['text'].apply(lambda x : remove_weird_words(x))


with open(fileN[:-5]+".tsv",'w') as write_tsv:
    #Eliminar tweets duplicados
    tweet_df.drop_duplicates(subset=["text"],inplace=True)

    write_tsv.write(tweet_df.to_csv(sep='\t', index=False))

