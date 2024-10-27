import asyncpraw
from mastodon import Mastodon
from datetime import datetime
from typing import Dict, List
import json
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        # Print credentials for debugging (remove in production)
        print(f"Initializing Reddit collector with client_id: {client_id[:5]}...")
        
        self.reddit = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    async def collect_data(self, keywords: List[str]) -> List[SocialPost]:
        posts = []
        try:
            for keyword in keywords:
                print(f"Searching Reddit for keyword: {keyword}")
                subreddit = await self.reddit.subreddit('all')
                async for submission in subreddit.search(keyword, limit=100):
                    author_name = '[deleted]'
                    if hasattr(submission, 'author') and submission.author:
                        author_name = submission.author.name

                    post = SocialPost(
                        platform='reddit',
                        post_id=submission.id,
                        content=submission.selftext if submission.selftext else submission.title,
                        timestamp=datetime.fromtimestamp(submission.created_utc),
                        author=author_name,
                        engagement={
                            'upvotes': submission.score,
                            'comments': submission.num_comments
                        },
                        keywords=[keyword]
                    )
                    posts.append(post)
                    print(f"Collected Reddit post: {post.post_id}")
        except Exception as e:
            print(f"Error collecting Reddit data: {str(e)}")
            print(f"Full error details: {repr(e)}")
        finally:
            await self.reddit.close()
        
        return posts

class MastodonCollector(PlatformCollector):
    def __init__(self, api_base_url: str, access_token: str):
        print(f"Initializing Mastodon collector with base URL: {api_base_url}")
        self.mastodon = Mastodon(
            api_base_url=api_base_url,
            access_token=access_token
        )

    async def collect_data(self, keywords: List[str]) -> List[SocialPost]:
        posts = []
        try:
            for keyword in keywords:
                print(f"Searching Mastodon for keyword: {keyword}")
                results = self.mastodon.timeline_hashtag(keyword)
                for toot in results:
                    # Handle the case where created_at is already a datetime
                    if isinstance(toot['created_at'], datetime):
                        timestamp = toot['created_at']
                    else:
                        # Parse string timestamp
                        timestamp = datetime.strptime(toot['created_at'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    
                    post = SocialPost(
                        platform='mastodon',
                        post_id=str(toot['id']),
                        content=toot['content'],
                        timestamp=timestamp,
                        author=toot['account']['username'],
                        engagement={
                            'favorites': toot['favourites_count'],
                            'reblogs': toot['reblogs_count']
                        },
                        keywords=[keyword]
                    )
                    posts.append(post)
                    print(f"Collected Mastodon post: {post.post_id}")
        except Exception as e:
            print(f"Error collecting Mastodon data: {str(e)}")
            print(f"Full error details: {repr(e)}")
        
        return posts

class AsyncMongoDBHandler:
    def __init__(self, connection_string: str, db_name: str, collection_name: str):
        print(f"Initializing MongoDB connection to {db_name}.{collection_name}")
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def save_posts(self, posts: List[SocialPost]):
        """Save posts to MongoDB with upsert to avoid duplicates"""
        if not posts:
            print("No posts to save")
            return
            
        operations = []
        for post in posts:
            post_dict = post.to_dict()
            operations.append(
                UpdateOne(
                    {'platform': post.platform, 'post_id': post.post_id},
                    {'$set': post_dict},
                    upsert=True
                )
            )
        
        try:
            result = await self.collection.bulk_write(operations)
            print(f"Saved {len(posts)} posts to MongoDB")
            print(f"Modified: {result.modified_count}, Upserted: {result.upserted_count}")
        except Exception as e:
            print(f"Error saving to MongoDB: {str(e)}")

    async def get_stats(self) -> Dict:
        """Get basic statistics about the collected data"""
        try:
            total_posts = await self.collection.count_documents({})
            pipeline = [{'$group': {'_id': '$platform', 'count': {'$sum': 1}}}]
            platform_counts = await self.collection.aggregate(pipeline).to_list(None)
            earliest = await self.collection.find_one({}, sort=[('timestamp', 1)])
            latest = await self.collection.find_one({}, sort=[('timestamp', -1)])
            
            stats = {
                'total_posts': total_posts,
                'posts_by_platform': platform_counts,
                'earliest_post': earliest['timestamp'] if earliest else None,
                'latest_post': latest['timestamp'] if latest else None
            }
            print("Retrieved stats:", json.dumps(stats, default=str))
            return stats
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}

    async def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            await self.collection.create_index([('platform', 1), ('post_id', 1)], unique=True)
            await self.collection.create_index('timestamp')
            await self.collection.create_index('keywords')
            await self.collection.create_index('platform')
            print("Created MongoDB indexes")
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")
class SocialAggregator:
    def __init__(self, db_handler: AsyncMongoDBHandler):
        self.collectors: List[PlatformCollector] = []
        self.db_handler = db_handler
        print("Initialized SocialAggregator")

    def add_collector(self, collector: PlatformCollector):
        """Add a platform collector to the aggregator"""
        self.collectors.append(collector)
        print(f"Added collector: {collector.__class__.__name__}")

    async def collect_all_data(self, keywords: List[str]):
        """Collect data from all platforms and save to database"""
        all_posts = []
        
        # Collect data from each platform
        for collector in self.collectors:
            try:
                print(f"Collecting data using {collector.__class__.__name__}")
                posts = await collector.collect_data(keywords)
                all_posts.extend(posts)
                print(f"Collected {len(posts)} posts from {collector.__class__.__name__}")
            except Exception as e:
                print(f"Error collecting data from {collector.__class__.__name__}: {str(e)}")
        
        # Save all collected posts to database
        if all_posts:
            await self.db_handler.save_posts(all_posts)
            print(f"Saved total of {len(all_posts)} posts to database")
        else:
            print("No posts collected from any platform")

    async def get_stats(self) -> Dict:
        """Get statistics about collected data"""
        return await self.db_handler.get_stats()

async def main():
    # Load credentials from environment variables
    reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    reddit_username = os.getenv('REDDIT_USERNAME')
    mastodon_token = os.getenv('MASTODON_ACCESS_TOKEN')

    if not all([reddit_client_id, reddit_client_secret, reddit_username]):
        print("Missing Reddit credentials in environment variables")
        return

    # Initialize MongoDB handler
    mongodb_handler = AsyncMongoDBHandler(
        connection_string='mongodb://localhost:27017',
        db_name='disease_surveillance',
        collection_name='social_searcher_data'
    )
    
    # Create indexes
    await mongodb_handler.create_indexes()
    
    # Initialize aggregator
    aggregator = SocialAggregator(mongodb_handler)
    
    # Add platform collectors
    reddit_collector = RedditCollector(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=f'HealthMonitor/1.0 (by /u/{reddit_username})'
    )
    
    mastodon_collector = MastodonCollector(
        api_base_url='https://mastodon.social',
        access_token=mastodon_token if mastodon_token else 'YOUR_MASTODON_ACCESS_TOKEN'
    )
    
    aggregator.add_collector(reddit_collector)
    aggregator.add_collector(mastodon_collector)
    
    # Define health-related keywords
    keywords = ['covid', 'flu', 'symptoms', 'vaccine']
    
    # Collect data
    await aggregator.collect_all_data(keywords)
    
    # Print stats
    stats = await aggregator.get_stats()
    print(json.dumps(stats, default=str, indent=2))

if __name__ == "__main__":
    asyncio.run(main())