# weather/utils/geo.py

import logging
from functools import lru_cache
import os
from ipware import get_client_ip  # type: ignore
from django.contrib.gis.geoip2 import GeoIP2
from django_weather_app import settings

logger = logging.getLogger(__name__)

@lru_cache
def _geoip():
    """Return a cached GeoIP2 instance using the configured GEOIP_PATH."""
    return GeoIP2(settings.GEOIP_PATH)

def get_client_ip_address(request):
    """
    Return client IP or None.

    Uses django-ipware so it works behind proxies and CDNs.
    """

    ip, is_routable = get_client_ip(request)
    logger.debug("Client IP: %s, Is routable: %s", ip, is_routable)
    return ip if ip and is_routable else None

def get_city_by_ip(ip: str | None) -> str | None:
    """Return city name or None for invalid/unknown IP."""
    if not ip:
        return None
    try:
        geoip_instance = _geoip()
        result = geoip_instance.city(ip)
        logger.debug("Full GeoIP result: %s", result)
        city = result.get("city")
        logger.debug("GeoIP city lookup result: %s", city)
        return city
    except Exception:
        logger.warning("GeoIP lookup failed for IP %s", ip, exc_info=True)
        return None

def index(request):
    """
    Return city name based on client IP.
    In DEBUG mode on localhost, use test IP for GeoIP lookup when real IP is not available.
    """
    ip = get_client_ip_address(request)
    logger.debug("Client IP address: %s", ip)

    # In local development, use test IP if real IP is not available
    if settings.DEBUG and not ip:
        test_ip = os.getenv('DEV_TEST_IP')
        logger.debug("DEBUG mode: using test IP %s for GeoIP lookup", test_ip)
        city = get_city_by_ip(test_ip)
        # If GeoIP doesn't return a city, use default fallback
        if not city:
            city = "Helsinki"
            logger.debug("DEBUG mode: GeoIP didn't return city, using fallback 'Helsinki'")
    else:
        city = get_city_by_ip(ip)
        # If no city found in production, use Helsinki fallback
        if not city:
            city = "Helsinki"
            logger.debug("No city found for IP, using fallback city: Helsinki")

    logger.debug("City determined from request: %s", city)
    return city
