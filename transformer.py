import pandas as pd
from sqlalchemy import text
from db import engine
def load_last_30_hours(city):
    sql = text("""SELECT obs_time, temp_c, humidity_pct, pressure_hpa, wind_speed_mps, precipitation_mm
                 FROM weather_obs
                 WHERE city = :city AND obs_time >= now() - interval '30 days'
                 ORDER BY obs_time""")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={'city': city})
    if df.empty:
        return df
    df['obs_time'] = pd.to_datetime(df['obs_time'])
    df = df.set_index('obs_time').sort_index()
    df = df.resample('H').mean()
    df['temp_c'] = df['temp_c'].interpolate(limit=6)
    df['humidity_pct'] = df['humidity_pct'].interpolate(limit=6)
    return df
def add_features(df):
    df = df.copy()
    df['hour'] = df.index.hour
    df['dayofyear'] = df.index.dayofyear
    df['lag_1'] = df['temp_c'].shift(1)
    df['lag_24'] = df['temp_c'].shift(24)
    df['rolling_24_mean'] = df['temp_c'].rolling(24).mean()
    df['rolling_72_mean'] = df['temp_c'].rolling(72).mean()
    df = df.dropna()
    return df
