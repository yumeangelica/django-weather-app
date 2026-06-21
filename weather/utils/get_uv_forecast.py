import logging
from datetime import datetime, timedelta, timezone

from weather.utils.openweather import geocode_city
from weather.utils.uv import estimate_uv_index

logger = logging.getLogger(__name__)


def get_uv_forecast(location: str, openweathermap_api_key: str):
    location_data = geocode_city(openweathermap_api_key, location)
    if not location_data:
        return None

    lat = location_data['lat']
    lon = location_data['lon']
    forecast = []

    for i in range(3):
        date = datetime.now(timezone.utc) + timedelta(days=i)
        forecast.append({
            'date': date.strftime("%Y-%m-%d"),
            'uv': estimate_uv_index(lat, lon, date),
        })

    return forecast
