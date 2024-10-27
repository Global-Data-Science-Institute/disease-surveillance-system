
# Social Media Data Collection for Public Health Diseases in Africa

This project collects social media data related to public health diseases in African countries, using keywords and country names to identify relevant posts. The data is stored in a MongoDB database and can be used for further analysis and insights into public health trends.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Customization](#customization)
- [Important Notes](#important-notes)

## Overview

The system uses Social Searcher's search capabilities and MongoDB to collect, filter, and store social media data on public health topics. It focuses on keywords associated with African countries and common diseases such as malaria, cholera, and COVID-19.

## Features

- **Collect Social Media Posts**: Scrapes social media posts related to specified public health topics and countries.
- **Keyword-Based Filtering**: Searches for African countries and public health keywords to narrow down relevant posts.
- **Storage in MongoDB**: Stores retrieved data for analysis or monitoring.
- **Customizable Query**: Modify keywords or countries in the script to adjust search parameters.

## Requirements

- **Python 3.x**
- **MongoDB** (running locally or on a server)
- **Python Libraries**:
  - `requests`
  - `beautifulsoup4`
  - `pymongo`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/africa-public-health-social-media.git
   cd africa-public-health-social-media
   ```

2. **Install Required Libraries**:
   ```bash
   pip install requests beautifulsoup4 pymongo
   ```

3. **Ensure MongoDB is Running**:
   - Start MongoDB on your local machine:
     ```bash
     mongod
     ```
   - Alternatively, use a MongoDB server instance if available.

## Usage

1. **Run the Script**:
   - To start collecting posts, use:
     ```bash
     python social_searcher_scraper.py
     ```

2. **Check MongoDB for Data**:
   - Open MongoDB shell or a GUI tool like MongoDB Compass to view stored data.
   - In the MongoDB shell, use:
     ```javascript
     use disease_surveillance
     db.social_searcher_data.find().pretty()
     ```

## Data Structure

Each social media post is stored as a document in MongoDB with the following structure:

```json
{
  "_id": ObjectId("..."),
  "text": "Post content related to public health.",
  "source": "Twitter",
  "timestamp": 1698256298.231, 
}
```

- **text**: The content of the social media post.
- **source**: The platform where the post was found.
- **timestamp**: The time of storage for tracking when the data was collected.

## Customization

- **Change Keywords and Countries**: Edit the `africa_countries` and `disease_keywords` lists in `social_searcher_scraper.py` to adjust the search query.
- **Adjust Search Depth**: Modify `page_limit` in the `scrape_social_searcher` function to control how many pages of results to scrape.

## Important Notes

- **Respect Rate Limits**: Avoid rapid requests to Social Searcher to prevent being blocked. Use `time.sleep()` for respectful delays between requests.
- **API Option**: Consider using Social Searcher’s [paid API](https://www.social-searcher.com/api/) for a more robust solution and full access to their data without scraping.
- **Compliance**: Web scraping is for educational purposes and may violate terms of service. Always prefer APIs if available.

---
