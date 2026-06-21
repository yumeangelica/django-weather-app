import logging

import requests

logger = logging.getLogger(__name__)

OPENWEATHERMAP_BASE_URL = 'https://api.openweathermap.org/data/2.5'
OPENWEATHERMAP_GEOCODING_URL = 'https://api.openweathermap.org/geo/1.0/direct'
OPENWEATHERMAP_TIMEOUT = 10


def fetch_openweathermap_json(url: str, params: dict) -> dict | list | None:
    try:
        response = requests.get(url, params=params, timeout=OPENWEATHERMAP_TIMEOUT)
    except requests.exceptions.Timeout:
        logger.warning("OpenWeatherMap request timed out for url=%s", url)
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning("OpenWeatherMap request failed for url=%s: %s", url, exc)
        return None

    try:
        payload = response.json()
    except ValueError:
        logger.warning("OpenWeatherMap returned invalid JSON for url=%s", url)
        return None

    if response.status_code != 200:
        message = payload.get('message', 'Unknown error') if isinstance(payload, dict) else 'Unknown error'
        logger.warning("OpenWeatherMap returned status=%s message=%s", response.status_code, message)
        return None

    return payload


def geocode_city(openweathermap_api_key: str, city: str) -> dict | None:
    if not openweathermap_api_key or not openweathermap_api_key.strip():
        logger.warning("OpenWeatherMap API key is missing.")
        return None

    payload = fetch_openweathermap_json(
        OPENWEATHERMAP_GEOCODING_URL,
        {
            'q': city,
            'limit': 1,
            'appid': openweathermap_api_key,
        },
    )

    if not isinstance(payload, list) or not payload:
        return None

    location = payload[0]
    if not isinstance(location, dict) or 'lat' not in location or 'lon' not in location:
        return None

    return location
