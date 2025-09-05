"""
TerraSynapse V2.0 - Motor de Integração
Combina dados de clima, satélite e mercado para análises inteligentes
"""

import asyncio
from typing import Dict, List
from datetime import datetime

class IntegrationEngine:
    def __init__(self):
        self.decision_rules = {
            "irrigation": self._analyze_irrigation_needs,
            "harvest": self._analyze_harvest_timing,
            "market": self._analyze_market_timing,
            "pest_risk": self._analyze_pest_risk
        }
    
    async def analyze(self, weather_data: Dict, satellite_data: Dict, market_data: Dict, culture: str) -> Dict:
        """
        Análise integrada combinando todos os dados
        Este é o diferencial da TerraSynapse - cruzar múltiplas fontes
        """
        
        # Extrair métricas chave
        current_temp = weather_data.get("current", {}).get("temperature", 25)
        humidity = weather_data.get("current", {}).get("humidity", 65)
        precipitation = weather_data.get("current", {}).get("precipitation", 0)
        
        ndvi = satellite_data.get("ndvi", {}).get("current", 0.6)
        vegetation_health = satellite_data.get("analysis", {}).get("vegetation_health", "good")
        
        price_trend = market_data.get("market_analysis", {}).get("trend", "sideways")
        price_change = market_data.get("prices", {}).get("monthly_change_percent", 0)
        
        # Análises integradas
        irrigation_analysis = await self._analyze_irrigation_needs(
            current_temp, humidity, precipitation, ndvi
        )
        
        pest_analysis = await self._analyze_pest_risk(
            current_temp, humidity, vegetation_health
        )
        
        market_analysis = await self._analyze_market_timing(
            price_trend, price_change, vegetation_health
        )
        
        harvest_analysis = await self._analyze_harvest_timing(
            ndvi, current_temp, price_trend, culture
        )
        
        # Recomendações prioritárias
        priority_actions = self._prioritize_actions([
            irrigation_analysis,
            pest_analysis,
            market_analysis,
            harvest_analysis
        ])
        
        # Score de risco geral
        risk_score = self._calculate_risk_score(
            weather_data, satellite_data, market_data
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._get_overall_status(risk_score),
            "risk_score": risk_score,
            "analyses": {
                "irrigation": irrigation_analysis,
                "pest_risk": pest_analysis,
                "market_timing": market_analysis,
                "harvest_timing": harvest_analysis
            },
            "priority_actions": priority_actions,
            "integrated_insights": self._generate_integrated_insights(
                weather_data, satellite_data, market_data
            ),
            "decision_support": self._generate_decision_support(
                irrigation_analysis, market_analysis, harvest_analysis
            )
        }
    
    async def _analyze_irrigation_needs(self, temp: float, humidity: float, precip: float, ndvi: float) -> Dict:
        """Análise integrada de necessidades de irrigação"""
        
        # Cálculo de estresse hídrico
        water_stress_score = 0
        
        if precip < 5:  # Pouca chuva
            water_stress_score += 3
        elif precip < 15:
            water_stress_score += 1
        
        if humidity < 50:  # Baixa umidade
            water_stress_score += 2
        elif humidity < 65:
            water_stress_score += 1
        
        if temp > 30:  # Alta temperatura
            water_stress_score += 2
        elif temp > 25:
            water_stress_score += 1
        
        if ndvi < 0.4:  # Vegetação estressada
            water_stress_score += 3
        elif ndvi < 0.6:
            water_stress_score += 1
        
        # Recomendação
        if water_stress_score >= 6:
            recommendation = "irrigate_immediately"
            urgency = "high"
        elif water_stress_score >= 3:
            recommendation = "irrigate_soon"
            urgency = "medium"
        else:
            recommendation = "monitor"
            urgency = "low"
        
        return {
            "water_stress_score": water_stress_score,
            "recommendation": recommendation,
            "urgency": urgency,
            "factors": {
                "precipitation": f"{precip}mm",
                "humidity": f"{humidity}%",
                "temperature": f"{temp}°C",
                "vegetation_index": ndvi
            },
            "action": self._get_irrigation_action(recommendation)
        }
    
    async def _analyze_pest_risk(self, temp: float, humidity: float, veg_health: str) -> Dict:
        """Análise de risco de pragas e doenças"""
        
        risk_score = 0
        risk_factors = []
        
        # Condições favoráveis para pragas
        if 20 <= temp <= 30 and humidity > 70:
            risk_score += 3
            risk_factors.append("Temperatura e umidade ideais para pragas")
        
        if humidity > 80:
            risk_score += 2
            risk_factors.append("Alta umidade favorece doenças fúngicas")
        
        if veg_health == "poor":
            risk_score += 3
            risk_factors.append("Vegetação estressada mais suscetível")
        
        # Determinar nível de risco
        if risk_score >= 5:
            risk_level = "high"
            recommendation = "immediate_inspection"
        elif risk_score >= 3:
            risk_level = "medium"
            recommendation = "weekly_monitoring"
        else:
            risk_level = "low"
            recommendation = "routine_monitoring"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendation": recommendation,
            "risk_factors": risk_factors,
            "preventive_actions": self._get_pest_prevention_actions(risk_level)
        }
    
    async def _analyze_market_timing(self, trend: str, price_change: float, veg_health: str) -> Dict:
        """Análise de timing de mercado"""
        
        # Lógica de timing de venda
        if trend == "bullish" and price_change > 5:
            if veg_health in ["good", "excellent"]:
                recommendation = "consider_selling"
                timing = "favorable"
            else:
                recommendation = "wait_for_harvest"
                timing = "wait"
        elif trend == "bearish" and price_change < -5:
            recommendation = "hold_product"
            timing = "unfavorable"
        else:
            recommendation = "monitor_market"
            timing = "neutral"
        
        return {
            "recommendation": recommendation,
            "timing": timing,
            "market_trend": trend,
            "price_change": price_change,
            "strategy": self._get_market_strategy(recommendation, trend)
        }
    
    async def _analyze_harvest_timing(self, ndvi: float, temp: float, price_trend: str, culture: str) -> Dict:
        """Análise de timing de colheita"""
        
        # Maturidade baseada em NDVI
        if ndvi > 0.7:
            maturity = "developing"
        elif ndvi > 0.5:
            maturity = "approaching_harvest"
        else:
            maturity = "harvest_ready"
        
        # Condições climáticas para colheita
        if temp < 35 and culture in ["soja", "milho"]:
            weather_suitable = True
        else:
            weather_suitable = False
        
        # Recomendação integrada
        if maturity == "harvest_ready" and weather_suitable and price_trend != "bearish":
            recommendation = "harvest_now"
            timing = "optimal"
        elif maturity == "approaching_harvest":
            recommendation = "prepare_harvest"
            timing = "upcoming"
        else:
            recommendation = "continue_monitoring"
            timing = "not_ready"
        
        return {
            "maturity_stage": maturity,
            "weather_suitable": weather_suitable,
            "recommendation": recommendation,
            "timing": timing,
            "estimated_days_to_harvest": self._estimate_harvest_days(ndvi, culture)
        }
    
    def _prioritize_actions(self, analyses: List[Dict]) -> List[Dict]:
        """Priorizar ações baseado em urgência"""
        
        actions = []
        
        # Irrigação
        irrigation = analyses[0]
        if irrigation["urgency"] == "high":
            actions.append({
                "priority": 1,
                "action": "Irrigation Required",
                "description": irrigation["action"],
                "urgency": "high"
            })
        
        # Pragas
        pest = analyses[1]
        if pest["risk_level"] == "high":
            actions.append({
                "priority": 2,
                "action": "Pest Monitoring",
                "description": pest["recommendation"],
                "urgency": "high"
            })
        
        # Mercado
        market = analyses[2]
        if market["timing"] == "favorable":
            actions.append({
                "priority": 3,
                "action": "Market Opportunity",
                "description": market["strategy"],
                "urgency": "medium"
            })
        
        # Colheita
        harvest = analyses[3]
        if harvest["timing"] == "optimal":
            actions.append({
                "priority": 1,
                "action": "Harvest Ready",
                "description": harvest["recommendation"],
                "urgency": "high"
            })
        
        return sorted(actions, key=lambda x: x["priority"])
    
    def _calculate_risk_score(self, weather_data: Dict, satellite_data: Dict, market_data: Dict) -> float:
        """Calcular score de risco geral (0-10)"""
        
        risk_factors = 0
        
        # Riscos climáticos
        temp = weather_data.get("current", {}).get("temperature", 25)
        precip = weather_data.get("current", {}).get("precipitation", 0)
        
        if temp > 35 or temp < 10:
            risk_factors += 2
        if precip > 50:  # Chuva excessiva
            risk_factors += 1
        if precip < 5:   # Seca
            risk_factors += 1
        
        # Riscos de vegetação
        ndvi = satellite_data.get("ndvi", {}).get("current", 0.6)
        if ndvi < 0.4:
            risk_factors += 2
        elif ndvi < 0.6:
            risk_factors += 1
        
        # Riscos de mercado
        price_change = market_data.get("prices", {}).get("monthly_change_percent", 0)
        if abs(price_change) > 10:  # Alta volatilidade
            risk_factors += 1
        
        return min(10.0, risk_factors)
    
    def _get_overall_status(self, risk_score: float) -> str:
        """Status geral baseado no score de risco"""
        
        if risk_score >= 7:
            return "high_risk"
        elif risk_score >= 4:
            return "moderate_risk"
        elif risk_score >= 2:
            return "low_risk"
        else:
            return "optimal"
    
    def _get_irrigation_action(self, recommendation: str) -> str:
        """Ação específica para irrigação"""
        
        actions = {
            "irrigate_immediately": "Iniciar irrigação nas próximas 2 horas",
            "irrigate_soon": "Programar irrigação para próximas 24 horas",
            "monitor": "Continuar monitoramento diário"
        }
        
        return actions.get(recommendation, "Monitorar condições")
    
    def _get_pest_prevention_actions(self, risk_level: str) -> List[str]:
        """Ações preventivas para pragas"""
        
        if risk_level == "high":
            return [
                "Inspeção visual diária das plantas",
                "Aplicação preventiva de fungicida",
                "Monitoramento de armadilhas",
                "Verificar sistema de drenagem"
            ]
        elif risk_level == "medium":
            return [
                "Inspeção semanal das culturas",
                "Manter área limpa de ervas daninhas",
                "Verificar plantas com sintomas"
            ]
        else:
            return [
                "Inspeção quinzenal de rotina",
                "Manter registros de observações"
            ]
    
    def _get_market_strategy(self, recommendation: str, trend: str) -> str:
        """Estratégia de mercado"""
        
        strategies = {
            "consider_selling": "Avaliar venda de parte da produção para aproveitar preços altos",
            "hold_product": "Manter produto armazenado aguardando melhores preços",
            "monitor_market": "Acompanhar diariamente oscilações de preço"
        }
        
        return strategies.get(recommendation, "Estratégia padrão de comercialização")
    
    def _estimate_harvest_days(self, ndvi: float, culture: str) -> int:
        """Estimar dias até colheita baseado em NDVI"""
        
        if ndvi > 0.7:
            return 45  # Ainda em desenvolvimento
        elif ndvi > 0.5:
            return 15  # Próximo da colheita
        else:
            return 0   # Pronto para colheita
    
    def _generate_integrated_insights(self, weather_data: Dict, satellite_data: Dict, market_data: Dict) -> List[str]:
        """Insights que só são possíveis com dados integrados"""
        
        insights = []
        
        # Insight: correlação clima + vegetação
        temp = weather_data.get("current", {}).get("temperature", 25)
        ndvi = satellite_data.get("ndvi", {}).get("current", 0.6)
        
        if temp > 30 and ndvi < 0.5:
            insights.append("Estresse térmico detectado: alta temperatura coincide com baixo NDVI")
        
        # Insight: timing mercado + maturação
        price_trend = market_data.get("market_analysis", {}).get("trend", "sideways")
        veg_health = satellite_data.get("analysis", {}).get("vegetation_health", "good")
        
        if price_trend == "bullish" and veg_health == "excellent":
            insights.append("Oportunidade ideal: preços em alta e cultura em excelente estado")
        
        # Insight: chuva + irrigação + custos
        precip = weather_data.get("current", {}).get("precipitation", 0)
        if precip > 20:
            insights.append("Precipitação abundante: oportunidade para reduzir custos de irrigação")
        
        return insights
    
    def _generate_decision_support(self, irrigation: Dict, market: Dict, harvest: Dict) -> Dict:
        """Sistema de apoio à decisão"""
        
        # Decisão principal baseada na análise integrada
        if harvest["timing"] == "optimal":
            main_decision = {
                "action": "COLHEITA",
                "priority": "ALTA",
                "reasoning": "Cultura pronta + condições favoráveis",
                "timeline": "Próximos 3-7 dias"
            }
        elif irrigation["urgency"] == "high":
            main_decision = {
                "action": "IRRIGAÇÃO",
                "priority": "ALTA", 
                "reasoning": "Estresse hídrico detectado",
                "timeline": "Próximas 24 horas"
            }
        elif market["timing"] == "favorable":
            main_decision = {
                "action": "COMERCIALIZAÇÃO",
                "priority": "MÉDIA",
                "reasoning": "Preços favoráveis no mercado",
                "timeline": "Próximas 2 semanas"
            }
        else:
            main_decision = {
                "action": "MONITORAMENTO",
                "priority": "BAIXA",
                "reasoning": "Condições estáveis",
                "timeline": "Rotina diária"
            }
        
        return {
            "main_decision": main_decision,
            "confidence_level": "alta",
            "data_quality": "boa",
            "next_review": "24 horas"
        }
    
    async def generate_alerts(self, analysis_data: Dict) -> List[Dict]:
        """Gerar alertas automáticos baseados na análise"""
        
        alerts = []
        
        # Alertas de irrigação
        irrigation = analysis_data.get("analysis", {}).get("irrigation", {})
        if irrigation.get("urgency") == "high":
            alerts.append({
                "type": "irrigation",
                "severity": "high",
                "message": "Irrigação urgente necessária",
                "action": irrigation.get("action"),
                "timestamp": datetime.now().isoformat()
            })
        
        # Alertas de pragas
        pest = analysis_data.get("analysis", {}).get("pest_risk", {})
        if pest.get("risk_level") == "high":
            alerts.append({
                "type": "pest",
                "severity": "medium",
                "message": "Alto risco de pragas detectado",
                "action": "Realizar inspeção detalhada",
                "timestamp": datetime.now().isoformat()
            })
        
        # Alertas de mercado
        market = analysis_data.get("analysis", {}).get("market_timing", {})
        if market.get("timing") == "favorable":
            alerts.append({
                "type": "market",
                "severity": "low",
                "message": "Oportunidade de mercado identificada",
                "action": market.get("strategy"),
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts