from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from weather.utils.get_weather_with_uv import get_weather_with_uv
from weather.utils.get_weather_forecast import get_weather_forecast
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
openweathermap_api_key = os.getenv('OPENWEATHERMAP_API_KEY')

def index(request):
    """ Front page where the user can search for weather or forecast """

    error_message = None

    if request.method == "GET" and 'city' in request.GET:
        city = request.GET.get('city')
        option = request.GET.get('option')

        if option == "weather":
            weather = get_weather_with_uv(openweathermap_api_key, city) # type: ignore
            if weather:
                return weather_view(request, city)
            else:
                error_message = f'Sorry, the weather data for {city.capitalize()} could not be retrieved.'

        elif option == "forecast":
            forecast = get_weather_forecast(openweathermap_api_key, city) # type: ignore
            if forecast:
                return weather_forecast_view(request, city)
            else:
                error_message = f'Sorry, the forecast data for {city.capitalize()} could not be retrieved.'

    return render(request, 'index.html', {'error_message': error_message})

def weather_view(request, city):
    """ Display fetched weather for the city """

    weather = get_weather_with_uv(openweathermap_api_key, city) # type: ignore

    if weather:
        return render(request, 'weather.html', {'weather': weather, 'city': city})
    else:
        return HttpResponse(f'Sorry, the weather data for {city.capitalize()} could not be retrieved.')



def current_weather_view(request):
    """ Display fetched weather for the city based on GET request """

    city = request.GET.get('city')

    weather = get_weather_with_uv(openweathermap_api_key, city) # type: ignore

    if weather:
        return render(request, 'weather.html', {'weather': weather, 'city': city})
    else:
        return HttpResponse(f'Sorry, the weather data for {city.capitalize()} could not be retrieved.')


def weather_forecast_view(request, city):
    """ Display fetched weather forecast for the city """

    forecast = get_weather_forecast(openweathermap_api_key, city) # type: ignore

    if forecast:
        return render(request, 'forecast.html', {'forecast': forecast, 'city': city})
    else:
        return HttpResponse(f'Sorry, the forecast data for {city.capitalize()} could not be retrieved.')