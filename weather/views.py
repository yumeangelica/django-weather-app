# weather/views.py

from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
import os

from weather.utils.get_weather_with_uv import get_weather_with_uv
from weather.utils.get_weather_forecast import get_weather_forecast
from weather.utils import geo

# Load environment variables from .env file
load_dotenv()
openweathermap_api_key = os.getenv('OPENWEATHERMAP_API_KEY')

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
        if option == "weather":
            weather = get_weather_with_uv(openweathermap_api_key, city)  # type: ignore
            if weather:
                return render(request, 'current_weather.html', {'weather': weather, 'city': city})
            error_message = f'Sorry, the weather data for {city.capitalize()} could not be retrieved.'
        elif option == "forecast":
            forecast = get_weather_forecast(openweathermap_api_key, city)  # type: ignore
            if forecast:
                return render(request, 'forecast.html', {'forecast': forecast, 'city': city})
            error_message = f'Sorry, the forecast data for {city.capitalize()} could not be retrieved.'

    return render(request, 'index.html', {'error_message': error_message, 'city': city})

def current_weather_view(request):
    """Display fetched weather for the city determined by GeoIP (with Helsinki fallback in DEBUG)."""
    city = geo.index(request)

    if not city:
        return render(request, '404.html', {'error_message': 'Could not determine your city.'})

    weather = get_weather_with_uv(openweathermap_api_key, city)  # type: ignore
    if weather:
        return render(request, 'current_weather.html', {'weather': weather, 'city': city})
    return HttpResponse(f'Sorry, the weather data for {city.capitalize()} could not be retrieved.')