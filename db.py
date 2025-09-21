import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
DB_URI = os.getenv('DB_URI')
if not DB_URI:
    raise RuntimeError('Please set DB_URI in environment or .env file')
engine = create_engine(DB_URI, echo=False)
def insert_weather(record: dict):
    cols = ','.join(record.keys())
    vals = ','.join([f":{k}" for k in record.keys()])
    sql = text(f"INSERT INTO weather_obs ({cols}) VALUES ({vals})")
    with engine.begin() as conn:
        conn.execute(sql, **record)
