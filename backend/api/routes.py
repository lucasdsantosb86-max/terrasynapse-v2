# backend/api/routes.py
from typing import Optional, List
from fastapi import APIRouter, Query

# Serviços já existentes
from services.satellite_service import SatelliteService
from services.market_service import MarketService
from services.integration_engine import IntegrationEngine

router = APIRouter(prefix="/api", tags=["api"])

_sat = SatelliteService()
_mkt = MarketService()
_ie  = IntegrationEngine()

@router.get("/satellite/preview")
def satellite_preview(
    lat: float,
    lon: float,
    zoom: int = 6,
    date: Optional[str] = None
):
    """Retorna URL da tile NDVI (GIBS) para pré-visualização."""
    return _sat.ndvi_preview_tile(lat=lat, lon=lon, zoom=zoom, date=date)

@router.get("/market/basket")
def market_basket(
    keys: Optional[str] = Query(None, description="Lista separada por vírgula. Ex.: corn,soy,wheat")
):
    """
    Retorna último preço e variação de uma cesta.
    Padrão: corn, soy, wheat, coffee, sugar
    """
    klist: Optional[List[str]] = [k.strip() for k in keys.split(",")] if keys else None
    return _mkt.basket_latest(klist)

@router.get("/overview")
def overview(
    lat: float,
    lon: float,
    keys: Optional[str] = None,
    ndvi_zoom: int = 6,
    ndvi_date: Optional[str] = None
):
    """
    Snapshot integrado (clima + NDVI preview + mercado + alertas).
    """
    klist: Optional[List[str]] = [k.strip() for k in keys.split(",")] if keys else None
    return _ie.build_overview(
        lat=lat,
        lon=lon,
        market_keys=klist,
        ndvi_zoom=ndvi_zoom,
        ndvi_date=ndvi_date
    )
