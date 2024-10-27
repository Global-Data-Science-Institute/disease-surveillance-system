import tweepy
from pymongo import MongoClient

# Twitter API credentials from your Developer App
API_KEY = 'PazTdcExgJNBAWanwx4tr9JDF'             # Twitter API Key
API_SECRET_KEY = 'LacODwHlDn2gdu1ZnIQeg9emozrnfeqpqYOmkNh6SGJYj4twSr'    # Twitter API Secret Key
ACCESS_TOKEN = '1850056271971405826-QdfxwO7D6yQnIrmiqevJebwcErcTAW'            # Twitter Access Token
ACCESS_TOKEN_SECRET = 'F83BhgbwBPOIt9Da1jnOS5vXC33lrBni9dVduuNTqniBu' # Twitter Access Token Secret
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAN94wgEAAAAAY%2BVGiubFrqyOIB5roObk0GFu09Q%3DVZdScuMWIcZgW8XbHG6Y1F6We73knBYUBsAHwbBVmJcVCU4M3v'            # Twitter Bearer Token for API v2

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.disease_surveillance
collection = db.twitter_data  # Define the collection where tweets will be stored

# Authenticate with Twitter API v2 using Tweepy
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Define keywords for public health diseases and African countries
africa_countries = ["Kenya", "Nigeria", "South Africa", "Uganda", "Ghana", "Ethiopia", "Tanzania", "Rwanda", "Botswana", "Senegal", "Egypt", "Morocco"]
disease_keywords = ["malaria", "cholera", "HIV", "tuberculosis", "COVID-19", "ebola", "yellow fever", "measles", "typhoid", "dengue"]

# Function to build a query for public health diseases in Africa
def build_query():
    disease_query = " OR ".join(disease_keywords)
    return disease_query

# Function to retrieve and store tweets related to African diseases
def retrieve_and_store_tweets(query, count=100):
    try:
        tweets = client.search_recent_tweets(query=query, max_results=count, tweet_fields=["created_at", "text"], expansions="author_id")
        for tweet in tweets.data:
            # Check if tweet text mentions an African country and a disease keyword
            if any(country.lower() in tweet.text.lower() for country in africa_countries) and \
               any(disease in tweet.text.lower() for disease in disease_keywords):
                tweet_data = {
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "user_id": tweet.author_id,
                    "disease_mentions": [disease for disease in disease_keywords if disease in tweet.text.lower()],
                    "country_mentions": [country for country in africa_countries if country.lower() in tweet.text.lower()]
                }
                # Insert tweet data into MongoDB
                collection.insert_one(tweet_data)
                print(f"Tweet by user {tweet.author_id} stored in MongoDB.")
    except tweepy.TweepyException as e:
        print(f"Error retrieving tweets: {e}")

# Run the script with query focused on public health diseases
query = build_query()
retrieve_and_store_tweets(query, count=10)
