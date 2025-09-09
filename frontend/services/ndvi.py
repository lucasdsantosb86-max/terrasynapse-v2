# frontend/services/ndvi.py
import requests
import pandas as pd
from functools import lru_cache
import time

BASE = "http://api.agromonitoring.com/agro/1.0/ndvi/history"

@lru_cache(maxsize=32)
def get_ndvi(agromon_key: str, polygon_id: str, days: int = 60) -> pd.DataFrame:
    if not agromon_key or not polygon_id:
        return pd.DataFrame()
    t_end = int(time.time())
    t_start = t_end - days * 86400
    params = {"polyid": polygon_id, "start": t_start, "end": t_end, "appid": agromon_key}
    r = requests.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame([{"date": pd.to_datetime(x["dt"], unit="s"), "ndvi": x["data"]["mean"]} for x in data if "data" in x])
    return df.sort_values("date")
