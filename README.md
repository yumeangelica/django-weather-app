# Weather Forecast App

A Django-based web application that provides real-time weather data and a 3-day weather forecast for cities worldwide. The application integrates with the OpenWeatherMap API to display accurate and up-to-date information.

## Features

- **Search by City**: Enter a city name to retrieve current weather data and a detailed 3-day forecast.
- **Auto-Location**: Automatically detects your city based on IP address for instant weather data.
- **Current Weather**: Displays the temperature, feels-like temperature, humidity, wind speed, UV index, and cloudiness.
- **3-Day Forecast**: Shows an hourly breakdown of temperature, wind speed, humidity, and UV index for the next three days.
- **Sunrise & Sunset Times**: Provides the local times for sunrise and sunset.
- **UV Index**: Check the UV index for the current day and forecast days.
- **Docker Ready**: Fully containerized for easy deployment
- **Azure Compatible**: Ready for deployment to Azure Container Apps or App Service

## Technologies Used

- **Backend**: Django (Python) with Gunicorn
- **Frontend**: HTML, CSS (with responsive design)
- **Static Files**: WhiteNoise (compressed static file serving from the app)
- **Web Server**: Nginx (reverse proxy)
- **APIs**: [OpenWeatherMap API](https://openweathermap.org/api)
- **Geolocation**: GeoIP2 database for IP-based city detection
- **Containerization**: Docker & Docker Compose
- **Cloud**: Azure Container Apps / App Service ready

## Quick Start

### Docker (Recommended)

1. Clone this repository:

   ```bash
   git clone https://github.com/yumeangelica/django-weather-app.git
   cd django-weather-app
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your OpenWeatherMap API key
   ```

3. Run with Docker:

   ```bash
   docker-compose up --build
   ```

4. Open your browser: http://localhost

### Local Development

1. Clone and setup:

   ```bash
   git clone https://github.com/yumeangelica/django-weather-app.git
   cd django-weather-app
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   # Create .env file with:
   DEBUG=True
   SECRET_KEY=your-secret-key
   OPENWEATHERMAP_API_KEY=your-api-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DEV_TEST_IP=your-ip-for-testing  # Optional: for local geolocation testing
   ```

3. **Download GeoIP database**:

   - Follow instructions in `geoip/README.md` to download the GeoLite2 database
   - This is required for IP-based geolocation functionality

4. Run migrations and start the development server:

   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py runserver
   ```

5. Access the app: http://localhost:8000

**Development workflow:**

- Make changes to HTML/CSS/Python files
- Refresh your browser (Cmd+R / Ctrl+R) to see changes
- Django automatically restarts when Python files change

## Azure Deployment

For detailed Azure deployment instructions, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).

Quick Azure deployment:

```bash
# For Container Apps
./deploy-azure.sh

# For App Service
./deploy-azure-appservice.sh
```

## How It Works

1. **Auto-Detection**: App automatically detects your city based on IP address.
2. **Manual Search**: Type the name of any city to override auto-detection.
3. **Select an Option**: Choose between current weather or 3-day forecast.
4. **View Weather Data**: See real-time weather data or a detailed forecast.

## API Requirements

- **OpenWeatherMap API Key**: Free tier provides 1,000 calls/day
  - Current weather data
  - UV index data
  - Geographic coordinates
- **GeoIP2 Database**: MaxMind GeoLite2 database (included)
  - IP-based geolocation
  - City detection from IP addresses

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. For more information, see the LICENSE file in this repository.
