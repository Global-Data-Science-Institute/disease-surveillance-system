import requests
from pymongo import MongoClient

# API key for OpenWeather
API_KEY = "7fc6701f86b3a9c681b084d9059256c8"

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.disease_surveillance

# Function to get latitude and longitude for a city
def get_coordinates(city, country_code, state_code=None):
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    print(f"Geocoding URL: {geocode_url}")  # Log the URL to the terminal for debugging

    response = requests.get(geocode_url)
    data = response.json()
    
    if response.status_code == 200 and data:
        return data[0]['lat'], data[0]['lon']
    else:
        print(f"Error fetching coordinates for {city}, {country_code}: {data}")
        return None, None

# Function to retrieve weather data using latitude and longitude
def get_weather_data(lat, lon, exclude="minutely,hourly"):
    weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={API_KEY}"
    print(f"Weather Data URL: {weather_url}")  # Log the URL to the terminal for debugging

    response = requests.get(weather_url)
    data = response.json()
    
    if response.status_code == 200:
        return data
    else:
        print(f"Error fetching weather data: {data}")
        return None

# Main function to retrieve and store weather data for a specific city and country
def retrieve_and_store_weather(city, country_code, state_code=None):
    lat, lon = get_coordinates(city, country_code, state_code)
    if lat is None or lon is None:
        print(f"Could not retrieve coordinates for {city}, {country_code}")
        return
    
    weather_data = get_weather_data(lat, lon)
    if weather_data:
        db.weather_reports.insert_one({
            "city": city,
            "country_code": country_code,
            "latitude": lat,
            "longitude": lon,
            "weather_data": weather_data
        })
        print(f"Weather data for {city}, {country_code} has been stored in MongoDB.")
    else:
        print(f"Could not retrieve weather data for {city}, {country_code}")

# Example usage
retrieve_and_store_weather("Nairobi", "KE")