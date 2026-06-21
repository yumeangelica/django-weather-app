import math
from datetime import datetime, timezone

from django.conf import settings
from pysolar.solar import get_altitude


def estimate_uv_index(lat: float, lon: float, dt_utc: datetime, uv_peak: float | None = None) -> float:
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt_utc.astimezone(timezone.utc)

    peak_value = settings.UV_PEAK_VALUE if uv_peak is None else uv_peak
    altitude_deg = get_altitude(lat, lon, dt_utc)

    if altitude_deg <= 0:
        return 0.0

    return round(max(0.0, peak_value * math.sin(math.radians(altitude_deg))), 2)
