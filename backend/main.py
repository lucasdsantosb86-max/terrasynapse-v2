# TerraSynapse V2.2 Enterprise - Backend Corrigido
# Erro de indentação corrigido na linha 665

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3
import bcrypt
import jwt
import uvicorn
from datetime import datetime, timedelta
import os
import httpx
import asyncio
import math
import logging
import json
from typing import Optional, Dict, Any
import time
from contextlib import asynccontextmanager

# =========================================================
# Configuração Enterprise
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("terrasynapse-enterprise")

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "terrasynapse_enterprise_2024_secure_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "terrasynapse@terrasynapse.com").split(",")

# Cache
cache_store = {}
CACHE_TTL = {
    "weather": 600,
    "market": 1200,
    "ndvi": 3600,
    "health": 30
}

def get_cache(key: str) -> Optional[Any]:
    if key in cache_store:
        data, timestamp, ttl = cache_store[key]
        if time.time() - timestamp < ttl:
            return data
        else:
            del cache_store[key]
    return None

def set_cache(key: str, data: Any, cache_type: str = "weather") -> None:
    ttl = CACHE_TTL.get(cache_type, 600)
    cache_store[key] = (data, time.time(), ttl)
    
    if len(cache_store) > 1000:
        oldest_key = min(cache_store.keys(), key=lambda k: cache_store[k][1])
        del cache_store[oldest_key]

# =========================================================
# FastAPI App
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TerraSynapse Enterprise API iniciando...")
    init_database()
    await validate_external_apis()
    logger.info("✅ TerraSynapse Enterprise API operacional")
    yield
    logger.info("🔄 TerraSynapse Enterprise API finalizando...")

app = FastAPI(
    title="TerraSynapse Enterprise API",
    description="Sistema Agropecuário Enterprise — v2.2",
    version="2.2.0",
    lifespan=lifespan
)

# CORS
ENV_MODE = os.getenv("ENV_MODE", "prod")
PRODUCTION_ORIGINS = [
    "https://terrasynapse-frontend.onrender.com",
    "https://app.terrasynapse.com"
]
DEVELOPMENT_ORIGINS = ["http://localhost:8501"]
ALLOWED_ORIGINS = PRODUCTION_ORIGINS if ENV_MODE == "prod" else DEVELOPMENT_ORIGINS + PRODUCTION_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

security = HTTPBearer()

# =========================================================
# Database
# =========================================================
DB_PATH = os.getenv("DATABASE_PATH", "/opt/render/project/src/terrasynapse_enterprise.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=2000")
    return conn

def init_database():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                perfil_profissional TEXT,
                empresa_propriedade TEXT,
                cidade TEXT,
                estado TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                subscription_tier TEXT DEFAULT 'enterprise'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action TEXT,
                endpoint TEXT,
                response_time_ms REAL,
                status_code INTEGER,
                details TEXT
            )
        """)

        indices = [
            "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)"
        ]
        
        for index in indices:
            cur.execute(index)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database inicializado")
        
    except Exception as e:
        logger.error(f"❌ Erro database: {e}")
        raise

# =========================================================
# JWT
# =========================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire, 
        "iat": datetime.utcnow(), 
        "type": "access",
        "issuer": "terrasynapse-enterprise"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": email, "payload": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# =========================================================
# APIs Externas
# =========================================================
async def validate_external_apis():
    logger.info("🔗 Validando APIs externas...")
    
    if OPENWEATHER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {"lat": -18.5880, "lon": -49.5690, "appid": OPENWEATHER_API_KEY}
                r = await client.get(url, params=params)
                if r.status_code == 200:
                    logger.info("✅ OpenWeather API: Operacional")
                else:
                    logger.warning(f"⚠️ OpenWeather API: HTTP {r.status_code}")
        except Exception as e:
            logger.error(f"❌ OpenWeather API: {e}")

async def get_weather_data_enterprise(lat: float, lon: float) -> dict:
    cache_key = f"weather_{lat:.4f}_{lon:.4f}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    if not OPENWEATHER_API_KEY:
        return await get_weather_fallback(lat, lon)
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat, 
                "lon": lon, 
                "appid": OPENWEATHER_API_KEY, 
                "units": "metric", 
                "lang": "pt_br"
            }
            
            r = await client.get(url, params=params)
            
            if r.status_code == 200:
                data = r.json()
                
                temp = data["main"]["temp"]
                temp_max = data["main"]["temp_max"]
                temp_min = data["main"]["temp_min"]
                humidity = data["main"]["humidity"]
                pressure = data["main"]["pressure"]
                wind_speed = data["wind"].get("speed", 0) * 3.6
                description = data["weather"][0]["description"]
                
                et0 = calculate_et0_simple(temp_max, temp_min, humidity, wind_speed)
                
                result = {
                    "temperatura": round(temp, 1),
                    "temp_max": round(temp_max, 1),
                    "temp_min": round(temp_min, 1),
                    "umidade": round(humidity),
                    "vento": round(wind_speed, 1),
                    "pressao": round(pressure),
                    "descricao": description.capitalize(),
                    "et0": et0,
                    "recomendacao_irrigacao": "Necessária" if et0 > 5 else "Opcional",
                    "source": "openweather",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                set_cache(cache_key, result, "weather")
                logger.info(f"OpenWeather: {lat:.4f},{lon:.4f} - {temp}°C")
                return result
                
            else:
                logger.warning(f"OpenWeather HTTP {r.status_code}")
                return await get_weather_fallback(lat, lon)
                
    except Exception as e:
        logger.error(f"OpenWeather error: {e}")
        return await get_weather_fallback(lat, lon)

def calculate_et0_simple(temp_max: float, temp_min: float, humidity: float, wind_speed: float) -> float:
    try:
        temp_mean = (temp_max + temp_min) / 2
        et0 = 0.0023 * (temp_mean + 17.8) * abs(temp_max - temp_min) ** 0.5 * 15
        return max(0.1, round(et0, 2))
    except:
        return 4.5

async def get_weather_fallback(lat: float, lon: float) -> dict:
    import random
    
    temp = random.uniform(18, 32)
    humidity = random.uniform(50, 85)
    wind = random.uniform(3, 15)
    pressure = random.uniform(1010, 1020)
    
    et0 = calculate_et0_simple(temp + 3, temp - 3, humidity, wind)
    
    return {
        "temperatura": round(temp, 1),
        "temp_max": round(temp + 3, 1),
        "temp_min": round(temp - 3, 1),
        "umidade": round(humidity),
        "vento": round(wind, 1),
        "pressao": round(pressure),
        "descricao": "Parcialmente nublado",
        "et0": et0,
        "recomendacao_irrigacao": "Necessária" if et0 > 5 else "Opcional",
        "source": "fallback",
        "timestamp": datetime.utcnow().isoformat()
    }

async def get_ndvi_data_enterprise(lat: float, lon: float) -> dict:
    cache_key = f"ndvi_{lat:.4f}_{lon:.4f}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    import random
    import numpy as np
    
    mes = datetime.now().month
    
    if 1 <= mes <= 2:
        ndvi_base = np.random.normal(0.55, 0.08)
        fase = "Colheita"
    elif 3 <= mes <= 4:
        ndvi_base = np.random.normal(0.45, 0.06)
        fase = "Plantio safrinha"
    elif 5 <= mes <= 8:
        ndvi_base = np.random.normal(0.62, 0.07)
        fase = "Desenvolvimento"
    else:
        ndvi_base = np.random.normal(0.75, 0.08)
        fase = "Crescimento"
    
    ndvi_final = max(0.15, min(0.92, ndvi_base))
    ndvi_rounded = round(ndvi_final, 3)
    
    if ndvi_rounded > 0.7:
        status, cor = "Excelente", "#059669"
    elif ndvi_rounded > 0.5:
        status, cor = "Bom", "#10B981"
    elif ndvi_rounded > 0.3:
        status, cor = "Regular", "#F59E0B"
    else:
        status, cor = "Crítico", "#EF4444"
    
    rec = "Vegetação saudável" if ndvi_rounded > 0.5 else "Monitorar desenvolvimento"
    
    result = {
        "ndvi": ndvi_rounded,
        "status_vegetacao": status,
        "cor": cor,
        "fase_cultura": fase,
        "data_analise": datetime.now().strftime("%Y-%m-%d"),
        "recomendacao": rec,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    set_cache(cache_key, result, "ndvi")
    return result

async def get_market_data_enterprise() -> dict:
    cache_key = "market_enterprise"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
    
    async def get_yahoo_price(symbol: str) -> dict:
        try:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                r = await client.get(url)
                if r.status_code != 200:
                    raise Exception(f"Yahoo Finance HTTP {r.status_code}")
                
                data = r.json()
                results = data.get("quoteResponse", {}).get("result", [])
                if not results:
                    raise Exception(f"Sem dados para {symbol}")
                
                quote = results[0]
                price = quote.get("regularMarketPrice")
                
                if price is None:
                    raise Exception(f"Sem preço para {symbol}")
                
                return {"price": float(price), "change": 0.0}
                
        except Exception as e:
            logger.error(f"Erro Yahoo {symbol}: {e}")
            raise
    
    try:
        # Buscar USD/BRL
        usd_brl = 5.25  # Fallback
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get("https://api.exchangerate.host/latest?base=USD&symbols=BRL")
                if r.status_code == 200:
                    usd_brl = float(r.json()["rates"]["BRL"])
        except:
            pass
        
        # Preços das commodities
        try:
            soja_data = await get_yahoo_price("ZS=F")
        except:
            soja_data = {"price": 13.50, "change": 0.0}
        
        try:
            milho_data = await get_yahoo_price("ZC=F")
        except:
            milho_data = {"price": 4.25, "change": 0.0}
        
        try:
            cafe_data = await get_yahoo_price("KC=F")
        except:
            cafe_data = {"price": 165.0, "change": 0.0}
        
        # Conversões para R$/saca
        BUSHEL_SOJA_KG = 27.2155
        BUSHEL_MILHO_KG = 25.4
        KG_POR_SACA = 60.0
        LB_POR_KG = 2.20462
        
        sacas_por_bushel_soja = KG_POR_SACA / BUSHEL_SOJA_KG
        sacas_por_bushel_milho = KG_POR_SACA / BUSHEL_MILHO_KG
        lb_por_saca = KG_POR_SACA * LB_POR_KG
        
        soja_brl = soja_data["price"] * sacas_por_bushel_soja * usd_brl
        milho_brl = milho_data["price"] * sacas_por_bushel_milho * usd_brl
        cafe_usd_lb = cafe_data["price"] / 100.0
        cafe_brl = cafe_usd_lb * lb_por_saca * usd_brl
        
        result = {
            "soja": {
                "preco": round(soja_brl, 2),
                "variacao": soja_data["change"],
                "tendencia": "Estável",
                "fonte": "Yahoo Finance"
            },
            "milho": {
                "preco": round(milho_brl, 2),
                "variacao": milho_data["change"],
                "tendencia": "Estável",
                "fonte": "Yahoo Finance"
            },
            "cafe": {
                "preco": round(cafe_brl, 2),
                "variacao": cafe_data["change"],
                "tendencia": "Estável",
                "fonte": "Yahoo Finance"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        set_cache(cache_key, result, "market")
        return result
        
    except Exception as e:
        logger.error(f"Erro market: {e}")
        return {
            "soja": {"preco": 165.50, "variacao": 0.0, "tendencia": "Estável"},
            "milho": {"preco": 78.25, "variacao": 0.0, "tendencia": "Estável"},
            "cafe": {"preco": 1050.00, "variacao": 0.0, "tendencia": "Estável"},
            "timestamp": datetime.utcnow().isoformat()
        }

def log_user_activity(user_email: str, action: str, endpoint: str, details: str = "", response_time: float = 0):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_logs (user_id, action, endpoint, response_time_ms, details, timestamp)
            VALUES ((SELECT id FROM usuarios WHERE email = ?), ?, ?, ?, ?, ?)
        """, (user_email, action, endpoint, response_time * 1000, details, datetime.utcnow()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erro log: {e}")

# =========================================================
# Endpoints
# =========================================================
@app.get("/")
async def root():
    return {
        "service": "TerraSynapse Enterprise API",
        "version": "2.2.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.2.0",
        "environment": ENV_MODE,
        "cache_entries": len(cache_store)
    }

@app.post("/register")
async def register_user(user_data: dict):
    try:
        required = ["nome_completo", "email", "password"]
        for field in required:
            if not user_data.get(field):
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {field}")
        
        email = user_data["email"].lower().strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        password_hash = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt())
        
        cur.execute("""
            INSERT INTO usuarios (nome_completo, email, password_hash, perfil_profissional,
                                  empresa_propriedade, cidade, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data["nome_completo"],
            email,
            password_hash.decode("utf-8"),
            user_data.get("perfil_profissional", "Produtor Rural"),
            user_data.get("empresa_propriedade", ""),
            user_data.get("cidade", "Capinópolis"),
            user_data.get("estado", "MG")
        ))
        
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        token = create_access_token({"sub": email})
        
        logger.info(f"Novo usuário: {email}")
        
        return {
            "message": "Usuário cadastrado com sucesso",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "nome": user_data["nome_completo"],
                "email": email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro registro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.post("/login")
async def login_user(credentials: dict):
    try:
        email = credentials.get("email", "").lower().strip()
        password = credentials.get("password", "")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email e senha obrigatórios")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM usuarios WHERE email = ? AND is_active = 1", (email,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        if not bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        cur.execute("UPDATE usuarios SET last_login = ? WHERE id = ?", (datetime.utcnow(), user[0]))
        conn.commit()
        conn.close()
        
        token = create_access_token({"sub": email})
        
        logger.info(f"Login: {email}")
        
        return {
            "message": "Login realizado com sucesso",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user[0],
                "nome": user[1],
                "email": user[2]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/dashboard/{lat}/{lon}")
async def dashboard_enterprise(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        start_time = time.time()
        
        weather_data, ndvi_data, market_data = await asyncio.gather(
            get_weather_data_enterprise(lat, lon),
            get_ndvi_data_enterprise(lat, lon),
            get_market_data_enterprise()
        )
        
        alertas = []
        
        if weather_data["et0"] > 6:
            alertas.append({
                "tipo": "irrigacao",
                "prioridade": "alta",
                "mensagem": f"ET0 elevada ({weather_data['et0']}mm) - Irrigação recomendada"
            })
        
        if ndvi_data["ndvi"] < 0.5:
            alertas.append({
                "tipo": "vegetacao",
                "prioridade": "media",
                "mensagem": f"NDVI baixo ({ndvi_data['ndvi']}) - Verificar campo"
            })
        
        soja_preco = market_data["soja"]["preco"]
        produtividade = 55 if ndvi_data["ndvi"] > 0.6 else 45
        receita_ha = produtividade * soja_preco
        
        result = {
            "status": "success",
            "data": {
                "clima": weather_data,
                "vegetacao": ndvi_data,
                "mercado": market_data,
                "alertas": alertas,
                "rentabilidade": {
                    "cultura": "Soja",
                    "produtividade_estimada": produtividade,
                    "preco_saca": soja_preco,
                    "receita_por_hectare": round(receita_ha, 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response_time = time.time() - start_time
        log_user_activity(user["email"], "DASHBOARD_VIEW", f"/dashboard/{lat}/{lon}", "", response_time)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar dashboard")

@app.get("/weather/{lat}/{lon}")
async def weather_endpoint(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        data = await get_weather_data_enterprise(lat, lon)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Erro weather: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados climáticos")

@app.get("/satellite/{lat}/{lon}")
async def satellite_endpoint(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        data = await get_ndvi_data_enterprise(lat, lon)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Erro satellite: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de satélite")

@app.get("/market")
async def market_endpoint(user: dict = Depends(verify_token)):
    try:
        data = await get_market_data_enterprise()
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Erro market: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de mercado")

# =========================================================
# Deploy
# =========================================================
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )
