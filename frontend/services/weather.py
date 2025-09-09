# frontend/services/weather.py
from __future__ import annotations
import datetime as dt
import requests
import pandas as pd
from functools import lru_cache

OPEN_METEO = "https://api.open-meteo.com/v1/forecast"

@lru_cache(maxsize=64)
def get_weather(lat: float, lon: float, timezone: str = "auto") -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,windspeed_10m,pressure_msl",
        "daily": "et0_fao_evapotranspiration,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": 7,
        "forecast_days": 7,
        "timezone": timezone,
    }
    r = requests.get(OPEN_METEO, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    # montar DataFrames úteis
    daily = pd.DataFrame(data["daily"])
    hourly = pd.DataFrame(data["hourly"])

    daily["time"] = pd.to_datetime(daily["time"])
    hourly["time"] = pd.to_datetime(hourly["time"])

    # métricas “atuais” simples
    now_row = hourly.iloc[-1]
    current = {
        "temperature": float(now_row["temperature_2m"]),
        "humidity": float(now_row["relative_humidity_2m"]),
        "wind": float(now_row["windspeed_10m"]),
        "pressure": float(now_row["pressure_msl"]),
        "timestamp": pd.Timestamp.utcnow().isoformat(),
    }

    return {
        "current": current,
        "daily": daily,
        "hourly": hourly,
        "raw": data,
    }
