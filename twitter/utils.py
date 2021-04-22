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
def get_search_tweets_list(api,query,num_of_results=100,geocode =None):
    '''Get the number of tweets for a search query string
    and returns them as a list of Tweepy Status Objects.
    NOTE: Returns a mininum of 100 tweets'''
    tweets = []
    if num_of_results < 100:
        search_limit = num_of_results
    else:
        search_limit = 100
    cursor = tweepy.Cursor(api.search,q=query,
                           count=search_limit,
                           lang="en",tweet_mode="extended",
                           geocode = geocode )
    
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
def dataframe_from_tweets(status_list):
    import pandas as pd
    pd.set_option('display.max_colwidth', 280)
    '''Take a list of Tweepy Status Objects or 
    Tweepy Search Results Object and returns a DataFrame. 
    The DataFrame will show the status object properties:
    status.name
    status.screen_name
    text
    date
    language
    location'''
    
    df = pd.DataFrame(columns = ['name','user_name','text','date','language','location'])
    
    for tweet in status_list:
        try:
            text = tweet.full_text
        except:
            text = tweet.text   
            
        df = df.append({'name': tweet.user.name,
                   'user_name':tweet.user.screen_name,
                   'text':text,
                   'date':tweet.created_at,
                   'language':tweet.lang,
                   'location':tweet.user.location},
                   ignore_index =True)
        
    return df

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
def visualise_sentiments(sentiments):
    '''
    Take a collection of Positive, Negative, Neutral values
    and create a bas plot to visualise the sentiment analysis
    Parameter:
    sentiments: An iterable collection of sentiments such as Pandas series
    '''
    import matplotlib.pyplot as plt
    from IPython.display import set_matplotlib_formats
    set_matplotlib_formats('svg')

    #Get a unique values and counts of the sentiments (series/list)
    sentiment_counts = sentiments.value_counts()

    # A pandas series has plotting functions....
    # The series.plot.bar() method returns a reference to an axes object 
    color =['xkcd:dark green blue','xkcd:deep turquoise',
            'xkcd:green teal','xkcd:strong pink','xkcd:deep aqua']
    	
    axes = sentiment_counts.plot.bar(color=color, figsize=(6,5))

 

    # matplotlib.axes documentation
    # https://matplotlib.org/3.1.1/api/axes_api.html
    axes.set_xlabel("Twitter user overall sentiment rating",color="#fd3c06")
    axes.set_ylabel("Number of tweets",color="#fd3c06")
    axes.set_title(sentiments.name, color="#fd3c06")
    
    
    
 

    # Set the upper/top y limit to the total number of tweets/sentiments analysed
    axes.set_ylim(top=sentiment_counts.sum())
   
 

    # Annotate the bars/patches with the value of the height of each bar
    for p in axes.patches:
        axes.annotate(format(p.get_height(), 'd'), 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 5), 
                       textcoords = 'offset points')

    #plt.patch.set_facecolor('xkcd:mint green')
   
    plt.xticks(ha="right")
    plt.tight_layout()
    plt.show()
 