from datetime import datetime, timezone

from weather.utils.uv import estimate_uv_index


def get_current_uv_index(openweathermap_api_key: str, lat: float, lon: float):
    return estimate_uv_index(lat, lon, datetime.now(timezone.utc))
