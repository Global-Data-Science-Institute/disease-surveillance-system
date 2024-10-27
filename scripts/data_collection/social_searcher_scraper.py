import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.disease_surveillance
collection = db.social_searcher_data

# Keywords for public health diseases and African countries
africa_countries = ["Kenya", "Nigeria", "South Africa", "Uganda", "Ghana", "Ethiopia", "Tanzania", "Rwanda", "Botswana", "Senegal", "Egypt", "Morocco"]
disease_keywords = ["malaria", "cholera", "HIV", "tuberculosis", "COVID-19", "ebola", "yellow fever", "measles", "typhoid", "dengue"]

# Function to build a query for public health diseases in Africa
def build_query():
    query_terms = disease_keywords + africa_countries
    return " OR ".join(query_terms)

# Function to scrape search results from Social Searcher
def scrape_social_searcher(query, page_limit=1):
    base_url = "https://www.social-searcher.com/social-search/"
    for page in range(1, page_limit + 1):
        url = f"{base_url}?q={query}&p={page}"
        print(f"Scraping URL: {url}")

        # Send a request to Social Searcher
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Parse results
        results = soup.find_all("div", class_="postContent")
        if not results:
            print("No results found or scraping blocked.")
            return

        for result in results:
            post_data = {
                "text": result.get_text(strip=True),
                "source": result.find_previous("span", class_="postType").get_text(strip=True),
                "timestamp": time.time(),
            }
            # Insert data into MongoDB
            collection.insert_one(post_data)
            print(f"Stored post from {post_data['source']}")
        
        # Respectful delay between requests
        time.sleep(2)

# Run the script with the public health query
query = build_query()
scrape_social_searcher(query, page_limit=2)  # Limit to 2 pages to avoid excessive requests
