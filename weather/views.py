# weather/views.py

import logging
from django.conf import settings
from django.shortcuts import render

from weather.utils.get_weather_with_uv import get_weather_with_uv
from weather.utils.get_weather_forecast import get_weather_forecast
from weather.utils import geo

logger = logging.getLogger(__name__)

# Maximum accepted length for a city name from user input.
MAX_CITY_LENGTH = 100

def is_valid_city(city: str) -> bool:
    """Return True if the city string is safe to use in an API lookup.

    Guards against empty input, overly long strings and control characters.
    Invalid input is treated the same as a failed lookup by the views.
    """
    if not city or len(city) > MAX_CITY_LENGTH:
        return False
    return not any(ord(char) < 32 for char in city)

def index(request):
    """Front page where the user can search for weather or forecast."""
    error_message = None
    city = request.GET.get('city', '').strip()

    # If no city in URL, try to determine it based on IP address
    if not city:
        detected_city = geo.index(request)
        if detected_city:
            city = detected_city

    if request.method == "GET" and 'city' in request.GET:
        option = request.GET.get('option')
        if not is_valid_city(city):
            error_message = 'Sorry, that does not look like a valid city name.'
        elif option == "weather":
            weather = get_weather_with_uv(settings.OPENWEATHERMAP_API_KEY, city)
            if weather:
                return render(request, 'current_weather.html', {'weather': weather, 'city': city})
            error_message = f'Sorry, the weather data for {city.capitalize()} could not be retrieved.'
        elif option == "forecast":
            forecast = get_weather_forecast(settings.OPENWEATHERMAP_API_KEY, city)
            if forecast:
                return render(request, 'forecast.html', {'forecast': forecast, 'city': city})
            error_message = f'Sorry, the forecast data for {city.capitalize()} could not be retrieved.'

    return render(request, 'index.html', {'error_message': error_message, 'city': city})

def current_weather_view(request):
    """Display fetched weather for the city determined by GeoIP (with Helsinki fallback in DEBUG)."""
    city = geo.index(request)

    if not is_valid_city(city):
        return render(request, '404.html', {'error_message': 'Could not determine your city.'}, status=404)

    weather = get_weather_with_uv(settings.OPENWEATHERMAP_API_KEY, city)
    if weather:
        return render(request, 'current_weather.html', {'weather': weather, 'city': city})
    return render(
        request,
        '404.html',
        {'error_message': f'Sorry, the weather data for {city.capitalize()} could not be retrieved.'},
        status=404,
    )

def custom_404(request, exception=None):
    """Handle 404 errors with custom page."""
    return render(request, '404.html', {'error_message': 'Page not found.'}, status=404)
