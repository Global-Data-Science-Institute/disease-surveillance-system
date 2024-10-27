import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine

# Connect to PostgreSQL and MongoDB
engine = create_engine('postgresql://user:password@localhost:5433/disease_surveillance')
client = MongoClient('localhost', 27017)
db = client.disease_surveillance

# Load health data from PostgreSQL
health_data = pd.read_sql('health_facility_reports', engine)

# Load regions data to get region names
regions = pd.read_sql("SELECT region_id, region_name AS location FROM regions", engine)

# Merge health_data with regions to add location information
health_data = pd.merge(health_data, regions, on="region_id", how="left")

# Load weather data from MongoDB and normalize JSON
weather_data = list(db.weather_reports.find())
weather_df = pd.json_normalize(
    weather_data,
    sep='_',
    meta=['city', 'country_code', 'latitude', 'longitude'],
    record_path=['weather_data', 'daily']  # Extract daily weather data if available
)

# Rename 'city' in weather data to 'location' for consistent merging
weather_df.rename(columns={'city': 'location'}, inplace=True)

# Merge health and weather data based on location
merged_data = pd.merge(
    health_data,
    weather_df,
    on='location',
    how='left'
)

# Preprocess Data (e.g., filter, handle missing values)
merged_data.dropna(inplace=True)
merged_data.reset_index(drop=True, inplace=True)

# Display merged data or save it as needed for downstream analysis
print(merged_data.head())
