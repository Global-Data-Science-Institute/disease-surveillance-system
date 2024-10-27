
# Disease Surveillance and Outbreak Prediction System

This project aims to provide a comprehensive Disease Surveillance and Outbreak Prediction System for Africa. The system integrates real-time data collection, processing, and predictive analytics to monitor, assess, and forecast potential public health outbreaks. The primary goal is to help authorities and health organizations take proactive measures for effective disease management.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Customization](#customization)
- [Important Notes](#important-notes)

## Overview

The system gathers data from multiple sources, including health facility reports, social media, and weather information. Through integration with machine learning models, it provides predictive analytics to forecast outbreak probabilities, visualize risk distribution, and send real-time alerts.

## Features

- **Real-Time Dashboard**: Displays active case monitoring, risk indicators, environmental conditions, and social media signals.
- **Predictive Analytics**: Outbreak forecasts, risk distribution maps, trend analysis, and analysis of contributing factors.
- **Data Integration**: Aggregates data from health facilities, social media, weather APIs, and news sources.
- **Interactive Visualizations**: Charts, maps, and interactive visuals for disease distribution, trends, and sentiment analysis.
- **Alert System**: Sends real-time alerts based on disease outbreak predictions.
- **API Endpoints**: Accessible endpoints for data submission, prediction retrieval, and alert access.

## Architecture

The system is divided into multiple phases and components, including:
1. **Data Collection & Processing**:
   - Collects and preprocesses data from health facility reports, weather sources, and social media platforms.
   - Data is stored in MongoDB and PostgreSQL for efficient retrieval and analysis.

2. **Prediction System**:
   - Implements machine learning models (Random Forest, LSTM, XGBoost) to predict outbreaks.
   - Uses temporal patterns, growth rates, and environmental factors as model features.

3. **Alert System**:
   - Generates alerts based on prediction thresholds and distributes location-specific notifications.
   - Sends alerts to users based on outbreak probability.

4. **Frontend Dashboard**:
   - Built with React, TypeScript, and Tailwind CSS.
   - Displays real-time data, risk assessments, and visualizations for easy interpretation.

## Requirements

- **Backend**: Python 3.11, FastAPI, GraphQL
- **Data Processing**: Apache Spark, Apache Kafka
- **Machine Learning**: PyTorch 2.x
- **Databases**: PostgreSQL, MongoDB, Redis
- **Infrastructure**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: GitHub Actions, ArgoCD

### Python Libraries
  - `requests`
  - `beautifulsoup4`
  - `pymongo`
  - `tweepy`
  - `SQLAlchemy`
  - `fastapi`
  - `pydantic`
  - `scikit-learn`
  - `pytorch`
  - `psycopg2-binary`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/disease-surveillance-system.git
   cd disease-surveillance-system
   ```

2. **Install Required Libraries**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Docker Containers**:
   - Ensure Docker and Docker Compose are installed, then start the containers:
     ```bash
     docker-compose up -d
     ```

4. **Initialize Databases**:
   - Connect to PostgreSQL and MongoDB containers, then run schema creation scripts and set up collections.

## Usage

1. **Run the Data Collection Script**:
   ```bash
   python scripts/data_collection/health_data.py
   ```

2. **Retrieve Weather Data**:
   - To fetch weather data using OpenWeather API:
     ```bash
     python scripts/data_collection/weather_data.py
     ```

3. **Check MongoDB for Stored Social Media Data**:
   - After running the social media script, verify the data in MongoDB:
     ```javascript
     use disease_surveillance
     db.social_media_data.find().pretty()
     ```

4. **Start the Frontend Dashboard**:
   - Navigate to the frontend directory and start the React app.
     ```bash
     cd frontend
     npm install
     npm start
     ```

## Data Structure

### Health Facility Data
```json
{
  "report_id": "unique_id",
  "disease_id": "id_ref",
  "country_id": "country_id_ref",
  "region_id": "region_id_ref",
  "cases": 123,
  "date_reported": "YYYY-MM-DD",
  "health_facility_id": "facility_id",
  "reporter_name": "John Doe",
  "reporter_contact": "contact_info"
}
```

### Weather Data
```json
{
  "city": "Nairobi",
  "country_code": "KE",
  "latitude": -1.286389,
  "longitude": 36.817223,
  "weather_data": { ... }
}
```

## Customization

- **Modify Disease or Country Lists**: Adjust keywords or country lists in the scripts for targeted data collection.
- **Adjust Prediction Model**: Modify model parameters in the `prediction_system` for custom outbreak forecasting.
- **Set API Keys and Environment Variables**: Store API keys (e.g., for OpenWeather, Twitter) in environment files or a secure vault.

## Important Notes

- **Rate Limits and Compliance**: For web scraping, use respectful request delays. When possible, use official APIs (e.g., Social Searcher, OpenWeather).
- **Data Privacy**: Ensure compliance with local data protection laws, especially when handling sensitive health information.
- **Scalability**: Consider container orchestration (e.g., Kubernetes) for scaling.

---
