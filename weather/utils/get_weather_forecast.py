import logging
from datetime import datetime, timedelta, timezone
from django.core.cache import cache
from weather.utils.openweather import OPENWEATHERMAP_BASE_URL, fetch_openweathermap_json, geocode_city
from weather.utils.uv import estimate_uv_index

logger = logging.getLogger(__name__)


def get_weather_forecast(openweathermap_api_key: str, city: str):
    if not openweathermap_api_key or not openweathermap_api_key.strip():
        logger.warning("OpenWeatherMap API key is missing.")
        return None

    cache_key = f'forecast_{city.strip().lower()}'
    forecasts_by_day = cache.get(cache_key)

    if forecasts_by_day:
        return forecasts_by_day

    try:
        location = geocode_city(openweathermap_api_key, city)
        if not location:
            return None

        lat = location['lat']
        lon = location['lon']
        response = fetch_openweathermap_json(
            f'{OPENWEATHERMAP_BASE_URL}/forecast',
            {
                'lat': lat,
                'lon': lon,
                'appid': openweathermap_api_key,
                'units': 'metric',
                'cnt': 24,
            },
        )

        if not isinstance(response, dict):
            return None

        timezone_offset = response.get('city', {}).get('timezone', 0)
        local_tz = timezone(timedelta(seconds=timezone_offset))
        forecasts_by_day = {}

        for item in response['list']:
            dt_utc = datetime.fromtimestamp(item['dt'], timezone.utc)
            dt = dt_utc.astimezone(local_tz)
            date_str = dt.strftime("%Y-%m-%d")
            formatted_date_str = dt.strftime("%a %d %b %Y")

            forecast = {
                'date': formatted_date_str,
                'hour': dt.strftime("%H"),
                'temperature': round(item['main']['temp']),
                'description': item['weather'][0]['description'],
                'humidity': round(item['main']['humidity']),
                'wind_speed': round(item['wind']['speed']),
                'icon': f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                'uv_index': estimate_uv_index(lat, lon, dt_utc),
            }

            if date_str not in forecasts_by_day:
                forecasts_by_day[date_str] = {
                    'formatted_date': formatted_date_str,
                    'forecasts': []
                }

            forecasts_by_day[date_str]['forecasts'].append(forecast)

        cache.set(cache_key, forecasts_by_day, timeout=3600)

        return forecasts_by_day

    except (KeyError, TypeError, IndexError, ValueError):
        logger.exception("Unexpected weather forecast response for city=%s", city)
        return None
