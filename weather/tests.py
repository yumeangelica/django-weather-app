from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from weather import views
from weather.utils import geo
from weather.utils.get_weather_forecast import get_weather_forecast
from weather.utils.get_weather_with_uv import get_weather_with_uv
from weather.utils.openweather import geocode_city
from weather.utils.uv import estimate_uv_index

TEST_STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


class FakeResponse:
    def __init__(self, payload=None, status_code=200, json_error=False):
        self.payload = payload
        self.status_code = status_code
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("Invalid JSON")
        return self.payload


def weather_payload():
    return {
        'coord': {'lat': 60.1699, 'lon': 24.9384},
        'weather': [{'description': 'clear sky', 'icon': '01d'}],
        'main': {
            'temp': 20.4,
            'feels_like': 19.8,
            'temp_max': 22.1,
            'temp_min': 18.9,
            'humidity': 55,
            'pressure': 1015,
        },
        'visibility': 10000,
        'wind': {'speed': 4.2, 'deg': 230},
        'rain': {'1h': 0.3},
        'clouds': {'all': 10},
        'dt': 1_719_993_600,
        'sys': {'sunrise': 1_719_979_200, 'sunset': 1_720_036_800},
        'timezone': 10_800,
        'name': 'Helsinki',
    }


def forecast_payload():
    return {
        'city': {
            'coord': {'lat': 60.1699, 'lon': 24.9384},
            'timezone': 10_800,
        },
        'list': [
            {
                'dt': 1_719_993_600,
                'main': {'temp': 20.4, 'humidity': 55},
                'weather': [{'description': 'clear sky', 'icon': '01d'}],
                'wind': {'speed': 4.2},
            },
            {
                'dt': 1_720_004_400,
                'main': {'temp': 18.2, 'humidity': 60},
                'weather': [{'description': 'few clouds', 'icon': '02d'}],
                'wind': {'speed': 3.8},
            },
        ],
    }


def view_weather_context():
    return {
        'date': 'Sun 21 Jun 2026',
        'temperature': 20,
        'feels_like': 19,
        'temp_max': 22,
        'temp_min': 18,
        'description': 'clear sky',
        'humidity': 55,
        'wind_speed': 4,
        'wind_direction': 230,
        'sunrise': '04:00:00',
        'sunset': '23:00:00',
        'uv_index': 4.2,
        'cloudiness': 10,
        'visibility': 10000,
        'rain': '0 mm',
        'snow': '0 mm',
    }


def view_forecast_context():
    return {
        '2026-06-21': {
            'formatted_date': 'Sun 21 Jun 2026',
            'forecasts': [
                {
                    'hour': '12',
                    'temperature': 20,
                    'description': 'clear sky',
                    'humidity': 55,
                    'wind_speed': 4,
                    'uv_index': 4.2,
                },
            ],
        },
    }


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'], STORAGES=TEST_STORAGES)
class WeatherViewTests(SimpleTestCase):
    def test_health_check_returns_json(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy', 'service': 'django-weather-app'})

    def test_invalid_city_input_shows_error_without_api_lookup(self):
        with patch('weather.views.get_weather_with_uv') as get_weather:
            response = self.client.get('/', {'city': 'Bad\nCity', 'option': 'weather'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid city name')
        get_weather.assert_not_called()

    @override_settings(OPENWEATHERMAP_API_KEY='test-key')
    def test_current_weather_link_urlencodes_city(self):
        with patch('weather.views.get_weather_with_uv', return_value=view_weather_context()):
            response = self.client.get('/', {'city': 'New York', 'option': 'weather'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'city=New%20York&option=forecast')

    @override_settings(OPENWEATHERMAP_API_KEY='test-key')
    def test_forecast_link_urlencodes_city(self):
        with patch('weather.views.get_weather_forecast', return_value=view_forecast_context()):
            response = self.client.get('/', {'city': 'New York', 'option': 'forecast'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'city=New%20York&option=weather')


class WeatherUtilityTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch('weather.utils.get_weather_with_uv.estimate_uv_index', return_value=4.2)
    @patch('weather.utils.openweather.requests.get')
    def test_current_weather_uses_geocoding_and_coordinates(self, requests_get, estimate_uv):
        requests_get.side_effect = [
            FakeResponse([{'name': 'Helsinki', 'lat': 60.1699, 'lon': 24.9384, 'country': 'FI'}]),
            FakeResponse(weather_payload()),
        ]

        weather = get_weather_with_uv('test-key', 'Helsinki')

        self.assertEqual(weather['city'], 'Helsinki')
        self.assertEqual(weather['temperature'], 20)
        self.assertEqual(weather['uv_index'], 4.2)
        self.assertEqual(weather['rain'], '0.3 mm')
        self.assertEqual(requests_get.call_args_list[0].kwargs['params']['q'], 'Helsinki')
        self.assertEqual(requests_get.call_args_list[1].kwargs['params']['lat'], 60.1699)
        self.assertNotIn('q', requests_get.call_args_list[1].kwargs['params'])
        estimate_uv.assert_called_once()

    @patch('weather.utils.openweather.requests.get')
    def test_current_weather_returns_none_when_api_key_missing(self, requests_get):
        self.assertIsNone(get_weather_with_uv('', 'Helsinki'))
        requests_get.assert_not_called()

    @patch('weather.utils.get_weather_forecast.estimate_uv_index', return_value=3.5)
    @patch('weather.utils.openweather.requests.get')
    def test_forecast_groups_entries_and_estimates_uv(self, requests_get, estimate_uv):
        requests_get.side_effect = [
            FakeResponse([{'name': 'Helsinki', 'lat': 60.1699, 'lon': 24.9384, 'country': 'FI'}]),
            FakeResponse(forecast_payload()),
        ]

        forecast = get_weather_forecast('test-key', 'Helsinki')

        self.assertEqual(len(forecast), 1)
        day = next(iter(forecast.values()))
        self.assertEqual(len(day['forecasts']), 2)
        self.assertEqual(day['forecasts'][0]['uv_index'], 3.5)
        self.assertEqual(requests_get.call_args_list[1].kwargs['params']['lat'], 60.1699)
        self.assertEqual(estimate_uv.call_count, 2)

    @patch('weather.utils.openweather.requests.get')
    def test_geocoding_handles_api_errors(self, requests_get):
        requests_get.return_value = FakeResponse({'message': 'invalid api key'}, status_code=401)

        self.assertIsNone(geocode_city('bad-key', 'Helsinki'))

    @override_settings(UV_PEAK_VALUE=8.0)
    @patch('weather.utils.uv.get_altitude', return_value=30)
    def test_uv_estimate_scales_with_solar_altitude(self, get_altitude):
        uv_index = estimate_uv_index(60.1699, 24.9384, datetime(2026, 6, 21, 12, tzinfo=timezone.utc))

        self.assertEqual(uv_index, 4.0)
        get_altitude.assert_called_once()

    @override_settings(UV_PEAK_VALUE=8.0)
    @patch('weather.utils.uv.get_altitude', return_value=-5)
    def test_uv_estimate_is_zero_when_sun_is_below_horizon(self, get_altitude):
        uv_index = estimate_uv_index(60.1699, 24.9384, datetime(2026, 12, 21, 0, tzinfo=timezone.utc))

        self.assertEqual(uv_index, 0.0)
        get_altitude.assert_called_once()

    def test_geoip_missing_database_returns_none(self):
        geo._geoip.cache_clear()
        with TemporaryDirectory() as temp_dir:
            with patch.object(geo.settings, 'GEOIP_PATH', Path(temp_dir)):
                self.assertIsNone(geo.get_city_by_ip('8.8.8.8'))
        geo._geoip.cache_clear()

    def test_city_validation_rejects_control_characters_and_long_values(self):
        self.assertFalse(views.is_valid_city('Bad\nCity'))
        self.assertFalse(views.is_valid_city('x' * (views.MAX_CITY_LENGTH + 1)))
        self.assertTrue(views.is_valid_city('New York'))
