"""Fetcher script for Vedant's project.
Backfill uses Open-Meteo archive (free). Current observation uses OpenWeatherMap (requires OWM_KEY).
Usage examples:
  python src/fetcher.py --backfill --lat 19.0760 --lon 72.8777 --city Mumbai
  python src/fetcher.py --now --lat 19.0760 --lon 72.8777 --city Mumbai
"""
import argparse, requests
from datetime import datetime, timedelta
from db import insert_weather
from dotenv import load_dotenv
import os
load_dotenv()
OWM_KEY = os.getenv('OWM_KEY')
OPEN_METEO_URL = 'https://archive-api.open-meteo.com/v1/archive'
def backfill_open_meteo(lat, lon, city):
    end = datetime.utcnow().date()
    start = end - timedelta(days=30)
    params = {
        'latitude': lat, 'longitude': lon,
        'start_date': start.isoformat(), 'end_date': (end - timedelta(days=1)).isoformat(),
        'hourly': 'temperature_2m,relativehumidity_2m,pressure_msl,windspeed_10m,winddirection_10m,precipitation',
        'timezone': 'UTC'
    }
    r = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    hourly = data.get('hourly', {})
    times = hourly.get('time', [])
    for i,t in enumerate(times):
        row = {
            'city': city, 'country': None,
            'obs_time': datetime.fromisoformat(t),
            'temp_c': float(hourly['temperature_2m'][i]) if hourly['temperature_2m'][i] is not None else None,
            'feels_like_c': None,
            'pressure_hpa': int(hourly['pressure_msl'][i]) if hourly.get('pressure_msl') else None,
            'humidity_pct': int(hourly['relativehumidity_2m'][i]) if hourly.get('relativehumidity_2m') else None,
            'wind_speed_mps': float(hourly['windspeed_10m'][i]) if hourly.get('windspeed_10m') else None,
            'wind_deg': int(hourly['winddirection_10m'][i]) if hourly.get('winddirection_10m') else None,
            'weather_main': None, 'weather_description': None,
            'precipitation_mm': float(hourly['precipitation'][i]) if hourly.get('precipitation') else 0.0,
            'source': 'open-meteo-archive'
        }
        try:
            insert_weather(row)
        except Exception as e:
            print('Insert failed:', e)
    print('Backfill complete.')
def fetch_now_openweathermap(lat, lon, city):
    if not OWM_KEY:
        print('OWM_KEY not set; skipping current fetch from OpenWeatherMap.')
        return
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'lat': lat, 'lon': lon, 'appid': OWM_KEY, 'units': 'metric'}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    d = r.json()
    row = {
        'city': city or d.get('name'),
        'country': d.get('sys', {}).get('country'),
        'obs_time': datetime.utcfromtimestamp(d.get('dt')),
        'temp_c': d.get('main', {}).get('temp'),
        'feels_like_c': d.get('main', {}).get('feels_like'),
        'pressure_hpa': d.get('main', {}).get('pressure'),
        'humidity_pct': d.get('main', {}).get('humidity'),
        'wind_speed_mps': d.get('wind', {}).get('speed'),
        'wind_deg': d.get('wind', {}).get('deg'),
        'weather_main': d.get('weather', [{}])[0].get('main'),
        'weather_description': d.get('weather', [{}])[0].get('description'),
        'precipitation_mm': 0.0,
        'source': 'openweathermap_current'
    }
    insert_weather(row)
    print('Inserted current observation from OpenWeatherMap.')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--backfill', action='store_true')
    parser.add_argument('--now', action='store_true')
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--city', type=str, default='Unknown')
    args = parser.parse_args()
    if args.backfill:
        backfill_open_meteo(args.lat, args.lon, args.city)
    if args.now:
        fetch_now_openweathermap(args.lat, args.lon, args.city)
