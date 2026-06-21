# GeoIP Database Setup

This directory can contain the MaxMind GeoLite2 City database for IP-based geolocation.

The database file is intentionally not committed to GitHub. This project is a showcase repository, so the code is public but the local/deployed GeoIP database should be supplied separately.

## Download Instructions

1. **Sign up for a free MaxMind account**:

   - Go to https://www.maxmind.com/en/geolite2/signup
   - Create a free account

2. **Download GeoLite2 City database**:

   - Log in to your MaxMind account
   - Go to "Download Files" section
   - Download "GeoLite2 City" in MMDB format
   - Extract the downloaded file

3. **Place the database file**:
   - Copy `GeoLite2-City.mmdb` to this directory
   - The final path should be: `geoip/GeoLite2-City.mmdb`

## When This File Is Used

- **Local development**: place `GeoLite2-City.mmdb` here on your machine.
- **GitHub**: the `.mmdb` file is ignored and should not be pushed.
- **Docker builds**: the `.mmdb` file is excluded from the default build context.
- **Hosted demo**: provide the file privately at `/app/geoip/GeoLite2-City.mmdb` with mounted storage, a private deployment artifact, or a host-specific download step.

If the file is missing, manual city search still works and automatic location detection falls back gracefully.

## File Structure

```
geoip/
├── README.md (this file)
└── GeoLite2-City.mmdb (download this file)
```

## Note

The GeoLite2 database is not included in the repository due to:

- Large file size (~70MB)
- MaxMind license requirements
- Regular updates needed

The application will use this database for automatic city detection based on user IP addresses.
