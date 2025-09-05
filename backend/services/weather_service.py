"""
TerraSynapse V2.0 - Serviço de Clima
Integração com múltiplas APIs meteorológicas gratuitas
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from datetime import datetime
import os

class WeatherService:
    def __init__(self):
        self.primary_api = "openmeteo"
        self.fallback_apis = ["weatherapi", "openweathermap"]
        
        # APIs Keys (gratuitas)
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.weatherapi_key = os.getenv("WEATHERAPI_KEY", "")
        
    async def health_check(self) -> str:
        """Verificar status do serviço"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current=temperature_2m", timeout=5) as response:
                    if response.status == 200:
                        return "healthy"
            return "degraded"
        except:
            return "unhealthy"
    
    async def get_weather_data(self, latitude: float, longitude: float) -> Dict:
        """
        Obter dados meteorológicos completos
        Inclui: temperatura, umidade, precipitação, vento, pressão, UV
        """
        
        # Tentar API primária primeiro
        try:
            data = await self._get_openmeteo_data(latitude, longitude)
            if data:
                return data
        except Exception as e:
            print(f"OpenMeteo failed: {e}")
        
        # Fallback para WeatherAPI
        try:
            data = await self._get_weatherapi_data(latitude, longitude)
            if data:
                return data
        except Exception as e:
            print(f"WeatherAPI failed: {e}")
        
        # Fallback para OpenWeatherMap
        try:
            data = await self._get_openweathermap_data(latitude, longitude)
            if data:
                return data
        except Exception as e:
            print(f"OpenWeatherMap failed: {e}")
        
        # Se todos falharam, retornar dados mocados
        return self._get_mock_weather_data(latitude, longitude)
    
    async def _get_openmeteo_data(self, lat: float, lon: float) -> Dict:
        """OpenMeteo - 100% gratuito, sem limites"""
        
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,pressure_msl,uv_index",
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto",
            "forecast_days": 7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_openmeteo_response(data)
                
        return None
    
    async def _get_weatherapi_data(self, lat: float, lon: float) -> Dict:
        """WeatherAPI - 1M calls/mês grátis"""
        
        if not self.weatherapi_key:
            return None
            
        url = f"http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": self.weatherapi_key,
            "q": f"{lat},{lon}",
            "days": 7,
            "aqi": "yes",
            "alerts": "yes"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_weatherapi_response(data)
                
        return None
    
    async def _get_openweathermap_data(self, lat: float, lon: float) -> Dict:
        """OpenWeatherMap - 1000 calls/dia grátis"""
        
        if not self.openweather_key:
            return None
            
        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.openweather_key,
            "units": "metric",
            "lang": "pt_br"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_openweathermap_response(data)
                
        return None
    
    def _format_openmeteo_response(self, data: Dict) -> Dict:
        """Formatar resposta do OpenMeteo"""
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        return {
            "source": "OpenMeteo",
            "timestamp": datetime.now().isoformat(),
            "current": {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation", 0),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "pressure": current.get("pressure_msl"),
                "uv_index": current.get("uv_index")
            },
            "forecast": {
                "next_24h": self._extract_24h_forecast(data.get("hourly", {})),
                "next_7_days": self._extract_7day_forecast(daily)
            },
            "agricultural_insights": self._generate_agro_insights(current, daily),
            "alerts": self._generate_weather_alerts(current, daily)
        }
    
    def _format_weatherapi_response(self, data: Dict) -> Dict:
        """Formatar resposta do WeatherAPI"""
        
        current = data.get("current", {})
        forecast = data.get("forecast", {}).get("forecastday", [])
        
        return {
            "source": "WeatherAPI",
            "timestamp": datetime.now().isoformat(),
            "current": {
                "temperature": current.get("temp_c"),
                "humidity": current.get("humidity"),
                "precipitation": current.get("precip_mm", 0),
                "wind_speed": current.get("wind_kph"),
                "wind_direction": current.get("wind_degree"),
                "pressure": current.get("pressure_mb"),
                "uv_index": current.get("uv")
            },
            "forecast": {
                "next_7_days": [
                    {
                        "date": day["date"],
                        "max_temp": day["day"]["maxtemp_c"],
                        "min_temp": day["day"]["mintemp_c"],
                        "precipitation": day["day"]["totalprecip_mm"],
                        "humidity": day["day"]["avghumidity"]
                    }
                    for day in forecast[:7]
                ]
            },
            "agricultural_insights": self._generate_agro_insights(current, {"temperature_2m_max": [current.get("temp_c")]}),
            "alerts": data.get("alerts", {}).get("alert", [])
        }
    
    def _format_openweathermap_response(self, data: Dict) -> Dict:
        """Formatar resposta do OpenWeatherMap"""
        
        current = data.get("list", [{}])[0] if data.get("list") else {}
        main = current.get("main", {})
        wind = current.get("wind", {})
        
        return {
            "source": "OpenWeatherMap",
            "timestamp": datetime.now().isoformat(),
            "current": {
                "temperature": main.get("temp"),
                "humidity": main.get("humidity"),
                "precipitation": current.get("rain", {}).get("3h", 0),
                "wind_speed": wind.get("speed"),
                "wind_direction": wind.get("deg"),
                "pressure": main.get("pressure")
            },
            "forecast": {
                "next_24h": data.get("list", [])[:8]  # 8 períodos de 3h = 24h
            },
            "agricultural_insights": self._generate_agro_insights(main, {}),
            "alerts": []
        }
    
    def _extract_24h_forecast(self, hourly: Dict) -> list:
        """Extrair previsão das próximas 24 horas"""
        
        temps = hourly.get("temperature_2m", [])[:24]
        precips = hourly.get("precipitation_probability", [])[:24]
        winds = hourly.get("wind_speed_10m", [])[:24]
        
        return [
            {
                "hour": i,
                "temperature": temps[i] if i < len(temps) else None,
                "precipitation_prob": precips[i] if i < len(precips) else None,
                "wind_speed": winds[i] if i < len(winds) else None
            }
            for i in range(24)
        ]
    
    def _extract_7day_forecast(self, daily: Dict) -> list:
        """Extrair previsão dos próximos 7 dias"""
        
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precips = daily.get("precipitation_sum", [])
        winds = daily.get("wind_speed_10m_max", [])
        
        return [
            {
                "date": dates[i] if i < len(dates) else None,
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "precipitation": precips[i] if i < len(precips) else None,
                "max_wind": winds[i] if i < len(winds) else None
            }
            for i in range(min(7, len(dates)))
        ]
    
    def _generate_agro_insights(self, current: Dict, daily: Dict) -> Dict:
        """Gerar insights agrícolas baseados no clima"""
        
        temp = current.get("temperature_2m") or current.get("temp")
        humidity = current.get("relative_humidity_2m") or current.get("humidity")
        precipitation = current.get("precipitation", 0)
        
        insights = {
            "irrigation_recommendation": "normal",
            "disease_risk": "low",
            "stress_risk": "low",
            "harvest_conditions": "good"
        }
        
        # Análise de irrigação
        if precipitation < 5 and humidity < 60:
            insights["irrigation_recommendation"] = "increase"
        elif precipitation > 20:
            insights["irrigation_recommendation"] = "reduce"
        
        # Análise de risco de doenças
        if humidity > 80 and temp and 20 <= temp <= 30:
            insights["disease_risk"] = "high"
        
        # Análise de estresse térmico
        if temp and temp > 35:
            insights["stress_risk"] = "high"
        elif temp and temp < 10:
            insights["stress_risk"] = "frost_risk"
        
        return insights
    
    def _generate_weather_alerts(self, current: Dict, daily: Dict) -> list:
        """Gerar alertas meteorológicos"""
        
        alerts = []
        temp = current.get("temperature_2m") or current.get("temp")
        precipitation = current.get("precipitation", 0)
        wind = current.get("wind_speed_10m") or current.get("wind_speed")
        
        # Alertas de temperatura
        if temp and temp > 40:
            alerts.append({
                "type": "temperature",
                "severity": "high",
                "message": f"Temperatura extrema: {temp}°C. Risco de estresse térmico nas culturas."
            })
        
        # Alertas de chuva intensa
        if precipitation > 50:
            alerts.append({
                "type": "precipitation",
                "severity": "medium",
                "message": f"Chuva intensa prevista: {precipitation}mm. Monitorar alagamentos."
            })
        
        # Alertas de vento
        if wind and wind > 60:
            alerts.append({
                "type": "wind",
                "severity": "high",
                "message": f"Vento forte: {wind} km/h. Risco de danos às culturas."
            })
        
        return alerts
    
    def _get_mock_weather_data(self, lat: float, lon: float) -> Dict:
        """Dados simulados em caso de falha de todas as APIs"""
        
        return {
            "source": "Mock Data",
            "timestamp": datetime.now().isoformat(),
            "current": {
                "temperature": 25.0,
                "humidity": 65,
                "precipitation": 0,
                "wind_speed": 10,
                "wind_direction": 180,
                "pressure": 1013
            },
            "forecast": {
                "next_7_days": []
            },
            "agricultural_insights": {
                "irrigation_recommendation": "normal",
                "disease_risk": "low",
                "stress_risk": "low"
            },
            "alerts": [],
            "note": "Dados simulados - APIs meteorológicas indisponíveis"
        }