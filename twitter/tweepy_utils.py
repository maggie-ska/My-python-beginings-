import keys, tweepy
from textblob import TextBlob, Blobber
from textblob.sentiments import NaiveBayesAnalyzer

##################################################################
#
##################################################################
def create_tweepy_api():
    '''Authentucate and return an tweepy API object'''
    auth = tweepy.OAuthHandler(keys.consumer_key,keys.consumer_key_secret)
    auth.set_access_token(keys.access_token,keys.access_token_secret)

    # We use the api object to call/use twitter api methods/functions
    return tweepy.API(auth,wait_on_rate_limit=True,
                      wait_on_rate_limit_notify=True)

##################################################################
#
##################################################################
def get_twitter_search_query():
    query = input("Enter query (you can include filters): ")
    print("The search query is: ", query)
    return query

##################################################################
#
##################################################################
def get_search_tweets_list(api,query,num_of_results=100):
    '''Get the number of tweets for a search query string
    and returns them as a list.
    NOTE: Returns a mininum of 100 tweets'''
    tweets = []
    if num_of_results < 100:
        search_limit = num_of_results
    else:
        search_limit = 100
    cursor = tweepy.Cursor(api.search,q=query,
                           count=search_limit,
                           lang="en",tweet_mode="extended")
    
    for tweet in cursor.items(num_of_results):
        tweets.append(tweet)
        
    return tweets
##################################################################
#
##################################################################
def get_tweet_texts(tweets):
    '''Returns a list of text in the a given list of tweets'''
    tweets_list = []
    for tweet in tweets:
        try:
            text = tweet.full_text
        except:
            text = tweet.text        
        tweets_list.append(text)
    return tweets_list

##################################################################
#
##################################################################
def dataframe_from_tweets():
    pass

##################################################################
#
##################################################################
def sentiment_rater(text_list, analyzer="vader",preprocessor=False):
    '''Returns a list of Positive, Negative, Neutral values 
       for each string in a given list of strings.
       
       Parameters:
       analyzer: string - "naivebayes","textblob", "vader".  Default is "vader".
       preprocessor: bool - True to clean text. Default is False.      
       '''
    # Returned list
    sentiments = []
    
    # If preprocessor is True then preprocess and clean the texts
    # in the provide text_list parameter.
    if preprocessor == True:
        import preprocessor as p
        text_list = [p.clean(text) for text in text_list]
        print("Text in the list has been cleaned. URL's, hastags etc have been removed.\n")
    
    if analyzer.lower() in ["naivebayes","naive","bayes","n"]:
        
        blobber = Blobber(analyzer=NaiveBayesAnalyzer())
        print("Using Naive Bayes Analyser with TextBlob")
        for text in text_list:
            
            blob_sentiment = blobber(text).sentiment
            if blob_sentiment.classification == "pos":
                sentiments.append("Positive")
            elif blob_sentiment.classification == "neg":
                sentiments.append("Negative")
            else:
                sentiments.append("Neutral")
                
    elif analyzer.lower() in ["textblob","blob","b"]:
        
        blobber = Blobber()
        
        print("Using default TextBlob sentiment analysis")
        for text in text_list:
            # May need to chaneg the positive/negative values
            polarity = blobber(text).sentiment.polarity            
            if polarity >= 0.05:
                sentiments.append("Positive")
            elif polarity < 0.05 and polarity > -0.05 :
                sentiments.append("Neutral")
            else:
                sentiments.append("Negative")
    else:
        
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        # Create a Vader SentimentIntensityAnalyzer object
        vader_analyzer = SentimentIntensityAnalyzer()
        
        print("Using Vader sentiment analysis")
        for text in text_list:
            
            compound = vader_analyzer.polarity_scores(text)["compound"]
            
            if compound >= 0.05:
                sentiments.append("Positive")
            elif compound < 0.05 and compound > -0.05 :
                sentiments.append("Neutral")
            else:
                sentiments.append("Negative")
    
    # Return the list of sentiments
    return sentiments

##################################################################
#
##################################################################