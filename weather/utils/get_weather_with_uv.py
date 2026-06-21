import logging
from datetime import datetime, timedelta, timezone
from django.core.cache import cache
from weather.utils.openweather import OPENWEATHERMAP_BASE_URL, fetch_openweathermap_json, geocode_city
from weather.utils.uv import estimate_uv_index

logger = logging.getLogger(__name__)


def _format_precipitation(value):
    if value in (None, ''):
        return '0 mm'
    if isinstance(value, int | float):
        return f'{value} mm'
    return value


def get_weather_with_uv(openweathermap_api_key: str, city: str):
    if not openweathermap_api_key or not openweathermap_api_key.strip():
        logger.warning("OpenWeatherMap API key is missing.")
        return None

    cache_key = f'weather_{city.strip().lower()}'
    weather = cache.get(cache_key)

    if weather:
        return weather

    try:
        location = geocode_city(openweathermap_api_key, city)
        if not location:
            return None

        lat = location['lat']
        lon = location['lon']
        response = fetch_openweathermap_json(
            f'{OPENWEATHERMAP_BASE_URL}/weather',
            {
                'lat': lat,
                'lon': lon,
                'appid': openweathermap_api_key,
                'units': 'metric',
            },
        )

        if not isinstance(response, dict):
            return None

        timezone_offset = response.get('timezone', 0)
        local_tz = timezone(timedelta(seconds=timezone_offset))
        current_time = datetime.fromtimestamp(response.get('dt', datetime.now(timezone.utc).timestamp()), local_tz)

        sunrise_time = datetime.fromtimestamp(response['sys']['sunrise'], local_tz).strftime("%H:%M:%S")
        sunset_time = datetime.fromtimestamp(response['sys']['sunset'], local_tz).strftime("%H:%M:%S")

        weather = {
            'city': response['name'],
            'date': current_time.strftime("%a %d %b %Y"),
            'temperature': round(response['main']['temp']),
            'feels_like': round(response['main']['feels_like']),
            'temp_max': round(response['main']['temp_max']),
            'temp_min': round(response['main']['temp_min']),
            'description': response['weather'][0]['description'],
            'humidity': response['main']['humidity'],
            'wind_speed': round(response['wind']['speed']),
            'wind_direction': response['wind']['deg'],
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'icon': response['weather'][0]['icon'],
            'uv_index': estimate_uv_index(lat, lon, datetime.now(timezone.utc)),
            'cloudiness': response['clouds']['all'],
            'visibility': response.get('visibility', 'N/A'),
            'rain': _format_precipitation(response.get('rain', {}).get('1h')),
            'snow': _format_precipitation(response.get('snow', {}).get('1h')),
        }

        cache.set(cache_key, weather, timeout=600)

        return weather

    except (KeyError, TypeError, IndexError, ValueError):
        logger.exception("Unexpected weather response for city=%s", city)
        return None
