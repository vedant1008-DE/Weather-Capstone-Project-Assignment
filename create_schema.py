from db import engine
from sqlalchemy import text
create_sql = text("""
CREATE TABLE IF NOT EXISTS weather_obs (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    country VARCHAR(50),
    obs_time TIMESTAMP WITHOUT TIME ZONE,
    temp_c REAL,
    feels_like_c REAL,
    pressure_hpa INTEGER,
    humidity_pct INTEGER,
    wind_speed_mps REAL,
    wind_deg INTEGER,
    weather_main VARCHAR(100),
    weather_description VARCHAR(255),
    precipitation_mm REAL,
    source VARCHAR(100),
    inserted_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_obs(city, obs_time);
""")
with engine.begin() as conn:
    conn.execute(create_sql)
print("Schema created (or already exists). Table: weather_obs")