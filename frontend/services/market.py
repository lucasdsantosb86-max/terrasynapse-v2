# frontend/services/market.py
from __future__ import annotations
import yfinance as yf
import pandas as pd

# Tickers contínuos (CBOT / ICE):
TICKERS = {
    "Soja":  "ZS=F",
    "Milho": "ZC=F",
    "Café":  "KC=F",
}

def _last_price(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    hist = t.history(period="10d", interval="1d")
    if hist.empty:
        return {"price": None, "change_pct": None}
    last = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
    change_pct = ((last - prev) / prev) * 100 if prev else 0.0
    return {"price": float(last), "change_pct": float(change_pct)}

def get_commodities() -> pd.DataFrame:
    rows = []
    for name, ticker in TICKERS.items():
        p = _last_price(ticker)
        rows.append({"name": name, "ticker": ticker, **p})
    return pd.DataFrame(rows)
