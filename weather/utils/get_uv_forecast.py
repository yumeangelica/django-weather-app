import logging
from requests import get
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def _default_uv_forecast():
    """Return moderate default UV values for the next 3 days."""
    forecast = []
    for i in range(3):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        forecast.append({'date': date_str, 'uv': 5})  # Default moderate UV
    return forecast

def get_uv_forecast(location: str, openweathermap_api_key: str):
    """
    Get UV forecast using OpenWeatherMap API
    """
    try:
        # First get coordinates for the location
        geo_url = f'http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={openweathermap_api_key}'
        geo_response = get(geo_url).json()

        if not isinstance(geo_response, list) or not geo_response:
            return None

        first = geo_response[0]
        if 'lat' not in first or 'lon' not in first:
            return None

        lat = first['lat']
        lon = first['lon']

        forecast = []

        # Get UV forecast for next 3 days
        for i in range(3):
            date = datetime.now() + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            # OpenWeatherMap UV API gives current UV index
            uv_url = f'http://api.openweathermap.org/data/2.5/uvi?appid={openweathermap_api_key}&lat={lat}&lon={lon}'
            uv_response = get(uv_url).json()

            # For forecast days beyond today, use a reasonable estimate
            # (OpenWeatherMap's UV API primarily gives current UV)
            uv_value = uv_response.get('value', 5) if isinstance(uv_response, dict) else 5  # Default to moderate UV

            # Adjust UV based on day (simple heuristic)
            if i == 0:  # Today
                pass  # Use actual value
            elif i == 1:  # Tomorrow
                uv_value = max(0, uv_value * 0.9)  # Slightly lower
            else:  # Day after
                uv_value = max(0, uv_value * 0.8)  # Lower still

            forecast.append({
                'date': date_str,
                'uv': round(uv_value, 1)
            })

        return forecast

    except Exception:
        logger.exception("Error fetching UV forecast for location=%s", location)
        # Return default moderate UV values if API fails
        return _default_uv_forecast()
