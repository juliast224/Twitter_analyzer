from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import re
import tweepy
import numpy as np
import pandas as pd
from pandasgui import show
import matplotlib.pyplot as plt

import twitter_credentials


#### TWITTER CLIENT ####
class TwitterClient ():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
        
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def search_tweets(self):
        search_list = []
        for search in Cursor(self.twitter_client.search, id=self.twitter_user).items():
            search_list.append(search)
        return search_list

    ###mit der Methode können die Freunde eines Users ausgegeben werden###
    #def get_friend_list(self, num_friends): 
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list



#### TWITTER AUTHENTICATER ####
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth
   
#### TWITTER STREAMER####
class TwitterStreamer():
    """
    Klasse, die live Tweets streamt und verarbeitet
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
        #abrufen einer hashtag liste, die die gesuchten Wörter enthält #
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
    
        stream.filter(track=hash_tag_list)

####TWITTER STREAM LISTENER#### 
class TwitterListener(StreamListener):
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print (data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
                print("Error on_data: %s" % str(e))

    def on_error(self, status):
        if status == 420:
            #gibt ein falsch zurück, wenn das rate limit auftaucht
            return False
        print (status)

class TweetAnalyzer():
    def cleanUpTweets(self, txt):
        txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
        txt = re.sub(r'#', '', txt)
        txt = re.sub(r'RT : ', '', txt)
        txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
        return txt

    def getTextSubjectivity(self, txt):
        return TextBlob(txt).sentiment.subjectivity

    def getTextPolarity(self, txt):
        return TextBlob(txt).sentiment.polarity

    def getTextAnalysis(self, a):
        if a < 0:
            return "Negative"
        elif a == 0:
            return "Neutral"
        else:
            return "Positive"

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        df.index = np.arange(1, len(df)+1)

        df['clean_tweets'] = df['tweets'].apply(self.cleanUpTweets)
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['author'] = np.array([tweet.user.name for tweet in tweets])
        df['subjectivity'] = df['clean_tweets'].apply(self.getTextSubjectivity)
        df['polarity'] = df['clean_tweets'].apply(self.getTextPolarity)
        df['score'] = df['polarity'].apply(self.getTextAnalysis)

        ###gibt Kennzahlen aus, wenn man nicht mit PandasGUI arbeitet, sondern über die Python Ausgabe ###
        #print(np.mean(df['len'])
        #print(np.max(df['likes'])
        #print(np.min(df['retweets'])

        return df

if __name__=="__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="billgates", count=200, twitter_mode='extended')
    all_tweets = []
    all_tweets.extend(tweets)
    oldest_id = all_tweets[-1].id - 1
    while len(tweets) > 0:
        print("getting tweets before %s" % (oldest_id))
        tweets = api.user_timeline(screen_name="billgates", count=200, twitter_mode="extended", max_id=oldest_id)
        all_tweets.extend(tweets)
        oldest_id = all_tweets[-1].id - 1
        print("...%s downloaded so far" % (len(all_tweets)))
    Timeline = tweet_analyzer.tweets_to_data_frame(all_tweets)
    df = Timeline
    df.to_excel("output.xlsx")
    df.to_csv("output.csv")



    search_list = api.search(['#billgates'], lang='en', count=100)
    search_list_new = []
    search_list_new.extend(search_list)
    search_oldest_id = search_list_new[-1].id - 1
    while len(search_list) > 0:
        print("getting tweets before %s" % (search_oldest_id))
        search_list = api.search(['#billgates'], lang='en', count=100, max_id=search_oldest_id)
        search_list_new.extend(search_list)
        search_oldest_id = search_list_new[-1].id - 1
        print("...%s downloaded so far" % (len(search_list_new)))

    Search_list = tweet_analyzer.tweets_to_data_frame(search_list_new)
    df = Search_list
    df.to_excel("Stichwort.xlsx")

    show(Timeline, Search_list)

    ###gibt Graphen über die Python Ausgabe aus, wenn nicht mit PandasGUI gearbeitet wird ###
    #Timeline = tweet.analyzer.tweets_to_data_frame(all_tweets)
    #df = Timeline
    #time_likes = pd.Series(data=df['likes'].values, index=df['date'].values)
    #time_likes.plot(figsize=(16, 4), label="likes", legend=True)
    #plt.show()

    #time_retweets = pd.Series(data=df['retweets'].values, index=df['date'].values)
    #time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)
    #fig1 = plt.gcf()
    #plt.title('Time series - number of likes & retweets')
    #plt.show()

