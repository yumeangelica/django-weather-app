import logging
import requests

logger = logging.getLogger(__name__)

def get_current_uv_index(openweathermap_api_key: str, lat: float, lon: float):
    try:
        url = f'http://api.openweathermap.org/data/2.5/uvi?appid={openweathermap_api_key}&lat={lat}&lon={lon}'
        response = requests.get(url).json()
        if isinstance(response, dict):
            return response.get('value', 'N/A')  # Returns the UV index value from the response
        return "N/A"
    except Exception:
        logger.exception("Error fetching current UV index for lat=%s lon=%s", lat, lon)
        return "N/A"
