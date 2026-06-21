# Weather Forecast App

A Django-based web application that provides real-time weather data and a 3-day weather forecast for cities worldwide. The application integrates with the OpenWeatherMap API for weather data and estimates UV index values from solar position.

## Features

- **Search by City**: Enter a city name to retrieve current weather data and a detailed 3-day forecast.
- **Auto-Location**: Automatically detects your city based on IP address for instant weather data.
- **Current Weather**: Displays the temperature, feels-like temperature, humidity, wind speed, estimated UV index, and cloudiness.
- **3-Day Forecast**: Shows an hourly breakdown of temperature, wind speed, humidity, and estimated UV index for the next three days.
- **Sunrise & Sunset Times**: Provides the local times for sunrise and sunset.
- **Estimated UV Index**: Calculates UV estimates using solar position data without requiring a paid UV API.
- **Docker Ready**: Fully containerized for easy deployment
- **Azure Compatible**: Ready for deployment to Azure Container Apps or App Service

## Technologies Used

- **Backend**: Django (Python) with Gunicorn
- **Frontend**: HTML, CSS (with responsive design)
- **Static Files**: WhiteNoise (compressed static file serving from the app)
- **Web Server**: Nginx (reverse proxy)
- **APIs**: [OpenWeatherMap API](https://openweathermap.org/api)
- **UV Estimation**: pysolar-based solar position calculation
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
   # Edit .env with your OpenWeatherMap API key and Django secret key
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
   python3 -m pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   # Create .env file with:
   DEBUG=True
   SECRET_KEY=your-secret-key
   OPENWEATHERMAP_API_KEY=your-api-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   UV_PEAK_VALUE=8.0
   DEV_TEST_IP=your-ip-for-testing  # Optional: for local geolocation testing
   ```

3. **Download GeoIP database**:

   - Follow instructions in `geoip/README.md` to download the GeoLite2 database
   - This is required only for IP-based geolocation. Manual city search works without it.

4. Run migrations and start the development server:

   ```bash
   python3 manage.py migrate
   python3 manage.py collectstatic
   python3 manage.py runserver
   ```

5. Access the app: http://localhost:8000

**Development workflow:**

- Make changes to HTML/CSS/Python files
- Refresh your browser (Cmd+R / Ctrl+R) to see changes
- Django automatically restarts when Python files change

## Azure Deployment

For detailed Azure deployment instructions, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).

## GeoIP Database

This repository is a showcase of the application code, so the MaxMind GeoLite2 database is not committed to GitHub. The only tracked file in `geoip/` is the setup guide.

How the database is used:

- **GitHub showcase repo**: `geoip/GeoLite2-City.mmdb` is ignored by Git and is not pushed.
- **Local development**: download the database manually and place it at `geoip/GeoLite2-City.mmdb`. The app uses it automatically for IP-based city detection. Manual city search works even if the file is missing.
- **Docker builds**: `.dockerignore` excludes `*.mmdb`, so the local database is not copied into the Docker image by default.
- **Hosted demo**: the database is included only if the host/deploy setup provides it privately at `/app/geoip/GeoLite2-City.mmdb`, for example with mounted storage, a private deployment artifact, or a host-specific download step.

If a free-hosted demo, such as Azure for Students, does not provide the database file, the app still runs: manual city search works and auto-location falls back gracefully.

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

- **OpenWeatherMap API Key**: Free tier supports current weather, forecasts, and geocoding
  - Current weather data
  - 5-day / 3-hour forecast data
  - Geographic coordinates through the Geocoding API
- **Estimated UV Index**: Calculated from solar position with `pysolar`; this is an approximation, not measured UV sensor data.
- **GeoIP2 Database**: MaxMind GeoLite2 database (not included in Git)
  - IP-based geolocation
  - City detection from IP addresses when `geoip/GeoLite2-City.mmdb` is present

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. For more information, see the LICENSE file in this repository.
