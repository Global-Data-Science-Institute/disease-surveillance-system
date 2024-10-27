import praw
import requests
from mastodon import Mastodon
from datetime import datetime
from typing import Dict, List
import json
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pymongo import MongoClient
from pymongo.collection import Collection

@dataclass
class SocialPost:
    platform: str
    post_id: str
    content: str
    timestamp: datetime
    author: str
    location: str = None
    engagement: Dict = None
    keywords: List[str] = None

    def to_dict(self):
        return asdict(self)

class PlatformCollector(ABC):
    @abstractmethod
    async def collect_data(self, keywords: List[str]) -> List[SocialPost]:
        pass

class RedditCollector(PlatformCollector):
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    async def collect_data(self, keywords: List[str]) -> List[SocialPost]:
        posts = []
        for keyword in keywords:
            for submission in self.reddit.subreddit('all').search(keyword, limit=100):
                post = SocialPost(
                    platform='reddit',
                    post_id=submission.id,
                    content=submission.selftext,
                    timestamp=datetime.fromtimestamp(submission.created_utc),
                    author=submission.author.name if submission.author else '[deleted]',
                    engagement={
                        'upvotes': submission.score,
                        'comments': submission.num_comments
                    },
                    keywords=[keyword]
                )
                posts.append(post)
        return posts

class MastodonCollector(PlatformCollector):
    def __init__(self, api_base_url: str, access_token: str):
        self.mastodon = Mastodon(
            api_base_url=api_base_url,
            access_token=access_token
        )

    async def collect_data(self, keywords: List[str]) -> List[SocialPost]:
        posts = []
        for keyword in keywords:
            results = self.mastodon.timeline_hashtag(keyword)
            for toot in results:
                post = SocialPost(
                    platform='mastodon',
                    post_id=toot['id'],
                    content=toot['content'],
                    timestamp=datetime.strptime(toot['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                    author=toot['account']['username'],
                    engagement={
                        'favorites': toot['favourites_count'],
                        'reblogs': toot['reblogs_count']
                    },
                    keywords=[keyword]
                )
                posts.append(post)
        return posts

class MongoDBHandler:
    def __init__(self, connection_string: str, db_name: str, collection_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_posts(self, posts: List[SocialPost]):
        """Save posts to MongoDB with upsert to avoid duplicates"""
        for post in posts:
            post_dict = post.to_dict()
            self.collection.update_one(
                {'platform': post.platform, 'post_id': post.post_id},
                {'$set': post_dict},
                upsert=True
            )

    def get_stats(self) -> Dict:
        """Get basic statistics about the collected data"""
        return {
            'total_posts': self.collection.count_documents({}),
            'posts_by_platform': list(self.collection.aggregate([
                {'$group': {'_id': '$platform', 'count': {'$sum': 1}}}
            ])),
            'earliest_post': self.collection.find_one({}, sort=[('timestamp', 1)])['timestamp'],
            'latest_post': self.collection.find_one({}, sort=[('timestamp', -1)])['timestamp']
        }

    def create_indexes(self):
        """Create indexes for better query performance"""
        self.collection.create_index([('platform', 1), ('post_id', 1)], unique=True)
        self.collection.create_index('timestamp')
        self.collection.create_index('keywords')
        self.collection.create_index('platform')

class SocialAggregator:
    def __init__(self, mongodb_handler: MongoDBHandler):
        self.collectors: List[PlatformCollector] = []
        self.mongodb_handler = mongodb_handler

    def add_collector(self, collector: PlatformCollector):
        self.collectors.append(collector)

    async def collect_all_data(self, keywords: List[str]):
        tasks = []
        for collector in self.collectors:
            tasks.append(collector.collect_data(keywords))
        
        results = await asyncio.gather(*tasks)
        all_posts = []
        for posts in results:
            all_posts.extend(posts)
        
        # Save to MongoDB
        self.mongodb_handler.save_posts(all_posts)

    def get_stats(self) -> Dict:
        return self.mongodb_handler.get_stats()

async def main():
    # Initialize MongoDB handler
    mongodb_handler = MongoDBHandler(
        connection_string='mongodb://localhost:27017',
        db_name='disease_surveillance',
        collection_name='social_searcher_data'
    )
    
    # Create indexes for better performance
    mongodb_handler.create_indexes()
    
    # Initialize aggregator
    aggregator = SocialAggregator(mongodb_handler)
    
    # Add platform collectors
    reddit_collector = RedditCollector(
        client_id='YOUR_REDDIT_CLIENT_ID',
        client_secret='YOUR_REDDIT_CLIENT_SECRET',
        user_agent='HealthMonitor/1.0'
    )
    mastodon_collector = MastodonCollector(
        api_base_url='https://mastodon.social',
        access_token='YOUR_MASTODON_ACCESS_TOKEN'
    )
    
    aggregator.add_collector(reddit_collector)
    aggregator.add_collector(mastodon_collector)
    
    # Define health-related keywords
    keywords = ['covid', 'flu', 'symptoms', 'vaccine']
    
    # Collect data
    await aggregator.collect_all_data(keywords)
    
    # Print stats
    print(json.dumps(aggregator.get_stats(), default=str, indent=2))

if __name__ == "__main__":
    asyncio.run(main())