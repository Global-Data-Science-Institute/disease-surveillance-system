import random
import pandas as pd
from sqlalchemy import create_engine, text

# Database connection setup
engine = create_engine('postgresql://user:password@localhost:5433/disease_surveillance')

# Define data for countries, regions, and diseases
countries_data = [
    {"country_name": "Kenya", "iso_code": "KEN", "continent": "Africa"},
    {"country_name": "Uganda", "iso_code": "UGA", "continent": "Africa"},
    {"country_name": "Tanzania", "iso_code": "TZA", "continent": "Africa"},
    {"country_name": "Nigeria", "iso_code": "NGA", "continent": "Africa"},
    {"country_name": "South Africa", "iso_code": "ZAF", "continent": "Africa"}
]

regions_data = {
    "Kenya": ["Nairobi", "Mombasa", "Kisumu"],
    "Uganda": ["Central", "Northern", "Western"],
    "Tanzania": ["Dar es Salaam", "Arusha", "Dodoma"],
    "Nigeria": ["Lagos", "Abuja", "Ibadan"],
    "South Africa": ["Gauteng", "Western Cape", "KwaZulu-Natal"]
}

diseases_data = ["Malaria", "Cholera", "COVID-19", "Dengue", "Typhoid"]

# Populate reference tables with upsert logic
def populate_reference_tables():
    with engine.begin() as conn:
        # Populate countries table
        for country in countries_data:
            conn.execute(
                text("""
                INSERT INTO countries (country_name, iso_code, continent)
                VALUES (:country_name, :iso_code, :continent)
                ON CONFLICT (country_name) DO UPDATE
                SET iso_code = EXCLUDED.iso_code,
                    continent = EXCLUDED.continent
                """),
                {"country_name": country["country_name"], "iso_code": country["iso_code"], "continent": country["continent"]}
            )
        print("Countries table populated.")

        # Populate regions table
        for country_name, regions in regions_data.items():
            country_id = conn.execute(
                text("SELECT country_id FROM countries WHERE country_name = :country_name"),
                {"country_name": country_name}
            ).scalar()
            
            for region_name in regions:
                conn.execute(
                    text("""
                    INSERT INTO regions (region_name, country_id)
                    VALUES (:region_name, :country_id)
                    ON CONFLICT (region_name, country_id) DO UPDATE
                    SET country_id = EXCLUDED.country_id
                    """),
                    {"region_name": region_name, "country_id": country_id}
                )
        print("Regions table populated.")

        # Populate diseases table
        for disease_name in diseases_data:
            conn.execute(
                text("""
                INSERT INTO diseases (disease_name)
                VALUES (:disease_name)
                ON CONFLICT (disease_name) DO UPDATE
                SET disease_name = EXCLUDED.disease_name
                """),
                {"disease_name": disease_name}
            )
        print("Diseases table populated.")

# Generate and insert health facility data
def generate_health_data(num_records=100):
    data = {
        'disease_id': [],
        'country_id': [],
        'region_id': [],
        'cases': [random.randint(1, 20) for _ in range(num_records)],
        'date_reported': pd.date_range(start='2023-01-01', periods=num_records).to_list()
    }

    with engine.connect() as conn:
        # Fetch reference data
        countries = conn.execute(text("SELECT country_id, country_name FROM countries")).fetchall()
        diseases = conn.execute(text("SELECT disease_id, disease_name FROM diseases")).fetchall()

        # Check for empty reference data
        if not countries or not diseases:
            raise ValueError("Reference tables (countries, diseases) are empty. Populate them before running this script.")

        # Generate records for health facility reports
        for _ in range(num_records):
            disease = random.choice(diseases)
            country = random.choice(countries)
            
            # Get regions for the selected country
            regions = conn.execute(text("""
                SELECT region_id, region_name FROM regions WHERE country_id = :country_id
            """), {"country_id": country.country_id}).fetchall()
            
            if not regions:
                raise ValueError(f"No regions found for country {country.country_name}. Ensure regions are populated.")

            region = random.choice(regions)

            # Append foreign key IDs to data
            data['disease_id'].append(disease.disease_id)
            data['country_id'].append(country.country_id)
            data['region_id'].append(region.region_id)

        # Convert data to DataFrame
        df = pd.DataFrame(data)
        print(f"Number of records to insert: {len(df)}")

        # Insert data with transaction management
        with engine.begin() as conn:
            df.to_sql('health_facility_reports', conn, if_exists='append', index=False, method='multi')
        print("Data insertion completed.")

# Populate reference tables and insert simulated health data
populate_reference_tables()
generate_health_data(num_records=100)

print("Simulated health facility data added to PostgreSQL.")
