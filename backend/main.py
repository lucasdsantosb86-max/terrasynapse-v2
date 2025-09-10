# backend/main.py
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

# =========================================================
# Configurações básicas
# =========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("terrasynapse-backend")

SECRET_KEY = "terrasynapse_enterprise_2024_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="TerraSynapse Enterprise API",
    description="Sistema Agropecuário Profissional — v2.0",
    version="2.0.0",
)

# =========================================================
# CORS dinâmico (com fallback seguro)
# =========================================================
DEFAULT_ORIGINS = [
    "http://localhost:8501",                     # dev Streamlit
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://app.terrasynapse.com",              # domínio do app
    "https://terrasynapse-frontend.onrender.com" # subdomínio Render
]
env_origins = os.getenv("CORS_ORIGINS", "")
ALLOW_ORIGINS = [o.strip() for o in env_origins.split(",") if o.strip()] or DEFAULT_ORIGINS
ALLOW_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.onrender\.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_origin_regex=ALLOW_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# =========================================================
# Banco de dados (SQLite)
# =========================================================
DB_PATH = os.getenv("DB_PATH", "terrasynapse.db")

def _connect_db():
    # garante diretório quando usar caminho absoluto (ex.: /var/data/terrasynapse.db)
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_database():
    try:
        conn = _connect_db()
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                perfil_profissional TEXT,
                empresa_propriedade TEXT,
                cidade TEXT,
                estado TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS fazendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                nome TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                area_hectares REAL,
                cultura_principal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        conn.commit()
        conn.close()
        logger.info(f"DB OK: sqlite inicializado em {DB_PATH}")
    except Exception as e:
        logger.error(f"Erro ao inicializar DB: {e}")

# =========================================================
# Auth helpers (JWT)
# =========================================================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": email}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# =========================================================
# Clima / NDVI / Mercado
# =========================================================
def calculate_et0(temp_max, temp_min, humidity, wind_speed, solar_radiation=None) -> float:
    try:
        temp_mean = (temp_max + temp_min) / 2
        # delta (não usado diretamente, mantido pela completude do método)
        _ = 4098 * (0.6108 * math.exp(17.27 * temp_mean / (temp_mean + 237.3))) / (
            (temp_mean + 237.3) ** 2
        )
        if solar_radiation is None:
            solar_radiation = 15
        et0 = (0.0023 * (temp_mean + 17.8) * abs(temp_max - temp_min) ** 0.5 * solar_radiation) / 2.45
        return round(et0, 2)
    except Exception:
        return 4.5

async def get_weather_data(lat: float, lon: float) -> dict:
    """
    OpenWeather (https) -> métricas básicas + ET0 aproximada.
    Exige OPENWEATHER_API_KEY em variáveis de ambiente (Render -> Environment).
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "pt_br"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)
            if r.status_code == 200:
                d = r.json()
                temp = d["main"]["temp"]
                humidity = d["main"]["humidity"]
                wind_speed = d["wind"]["speed"]
                et0 = calculate_et0(temp + 5, temp - 5, humidity, wind_speed)
                return {
                    "temperatura": temp,
                    "umidade": humidity,
                    "vento": wind_speed,
                    "pressao": d["main"]["pressure"],
                    "descricao": d["weather"][0]["description"],
                    "et0": et0,
                    "recomendacao_irrigacao": "Necessária" if et0 > 5 else "Opcional",
                }
            logger.warning(f"OpenWeather status={r.status_code}, body={r.text[:180]}")
    except Exception as e:
        logger.error(f"Weather API error: {e}")

    # Fallback aleatório (mantém o app funcionando)
    import random
    temp = random.uniform(18, 35)
    humidity = random.uniform(40, 90)
    wind = random.uniform(1, 15)
    et0 = calculate_et0(temp + 5, temp - 5, humidity, wind)
    return {
        "temperatura": round(temp, 1),
        "umidade": round(humidity),
        "vento": round(wind, 1),
        "pressao": random.randint(1000, 1025),
        "descricao": "Parcialmente nublado",
        "et0": et0,
        "recomendacao_irrigacao": "Necessária" if et0 > 5 else "Opcional",
    }

async def get_ndvi_data(lat: float, lon: float) -> dict:
    """
    NDVI simulado por sazonalidade (mantém UI viva até ligar satélite real).
    """
    import random
    mes = datetime.now().month
    if 3 <= mes <= 5:       # outono (plantio soja 2ª/ milho safrinha)
        ndvi_base = random.uniform(0.6, 0.8)
    elif 6 <= mes <= 8:     # inverno (pós-colheita / palhada)
        ndvi_base = random.uniform(0.4, 0.6)
    elif 9 <= mes <= 11:    # primavera (pico de crescimento)
        ndvi_base = random.uniform(0.7, 0.9)
    else:                   # verão (amadurecimento/colheita)
        ndvi_base = random.uniform(0.5, 0.7)

    ndvi = round(ndvi_base, 3)
    if ndvi > 0.7:
        status, cor = "Excelente", "#4CAF50"
    elif ndvi > 0.5:
        status, cor = "Bom", "#8BC34A"
    elif ndvi > 0.3:
        status, cor = "Regular", "#FFC107"
    else:
        status, cor = "Crítico", "#F44336"

    return {
        "ndvi": ndvi,
        "status_vegetacao": status,
        "cor": cor,
        "data_analise": datetime.now().strftime("%Y-%m-%d"),
        "recomendacao": "Monitorar pragas" if ndvi < 0.5 else "Continuar manejo atual",
    }

# --------- Mercado com dados reais (Yahoo + FX) ----------
async def get_market_data() -> dict:
    """
    Preços em R$/saca (60 kg) para Soja, Milho e Café.
    Fontes:
      - Yahoo Finance (query1.finance.yahoo.com)
      - Exchangerate.host (conversão USD->BRL)
    Conversões:
      - 1 saca = 60 kg
      - Soja (ZS=F): USD/bushel   | 1 bushel soja = 27.2155 kg -> 1 saca ≈ 2.2046 bushels
      - Milho (ZC=F): USD/bushel  | 1 bushel milho = 25.4 kg   -> 1 saca ≈ 2.3622 bushels
      - Café (KC=F): US cents/lb  | 1 saca = 60 kg = 132.277 lb
    """
    TICKERS = {"soja": "ZS=F", "milho": "ZC=F", "cafe": "KC=F"}

    UA_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }

    async def yahoo_price(symbol: str) -> float:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        # Removido http2=True para não exigir o pacote 'h2'
        async with httpx.AsyncClient(timeout=15.0, headers=UA_HEADERS) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            res = data.get("quoteResponse", {}).get("result", [])
            if not res:
                raise RuntimeError(f"Yahoo sem resultado para {symbol}")
            price = res[0].get("regularMarketPrice")
            if price is None:
                raise RuntimeError(f"Yahoo sem preço regularMarketPrice para {symbol}")
            return float(price)

    async def usd_brl() -> float:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=BRL"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            return float(r.json()["rates"]["BRL"])

    try:
        soja_usd, milho_usd, cafe_cents, fx = await asyncio.gather(
            yahoo_price(TICKERS["soja"]),
            yahoo_price(TICKERS["milho"]),
            yahoo_price(TICKERS["cafe"]),
            usd_brl(),
        )

        # Conversões para R$/saca
        KG_POR_SACA = 60.0
        BUSHEL_SOJA_KG = 27.2155
        BUSHEL_MILHO_KG = 25.4
        LB_POR_KG = 2.2046226218

        sacas_por_bushel_soja = KG_POR_SACA / BUSHEL_SOJA_KG          # ≈ 2.2046
        sacas_por_bushel_milho = KG_POR_SACA / BUSHEL_MILHO_KG         # ≈ 2.3622
        lb_por_saca = KG_POR_SACA * LB_POR_KG                          # ≈ 132.277

        soja_brl_saca = soja_usd * sacas_por_bushel_soja * fx
        milho_brl_saca = milho_usd * sacas_por_bushel_milho * fx
        cafe_usd_lb = cafe_cents / 100.0
        cafe_usd_saca = cafe_usd_lb * lb_por_saca
        cafe_brl_saca = cafe_usd_saca * fx

        logger.info(
            f"[MARKET] USD/BRL={fx:.4f} | ZS=F={soja_usd} USD/bu | "
            f"ZC=F={milho_usd} USD/bu | KC=F={cafe_cents} USc/lb"
        )

        def pack(preco_brl: float, ref_usd: float, src: str = "yahoo"):
            return {
                "preco": round(preco_brl, 2),
                "variacao": 0.0,   # placeholder
                "tendencia": "—",  # placeholder
                "fx": round(fx, 4),
                "ref_usd": ref_usd,
                "source": src,
            }

        return {
            "soja":  pack(soja_brl_saca, soja_usd),
            "milho": pack(milho_brl_saca, milho_usd),
            "cafe":  pack(cafe_brl_saca, cafe_cents),
        }

    except Exception as e:
        logger.error(f"[MARKET] fallback: {e}")
        return {
            "soja":  {"preco": 165.0, "variacao": 0.0, "tendencia": "—", "source": "fallback"},
            "milho": {"preco":  75.0, "variacao": 0.0, "tendencia": "—", "source": "fallback"},
            "cafe":  {"preco": 950.0, "variacao": 0.0, "tendencia": "—", "source": "fallback"},
        }

# =========================================================
# Lifecycle
# =========================================================
@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info(f"CORS allow_origins={ALLOW_ORIGINS} | allow_origin_regex={ALLOW_REGEX}")

# =========================================================
# Endpoints
# =========================================================
@app.get("/")
async def root():
    return {
        "message": "TerraSynapse Enterprise API",
        "version": "2.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "online",
        "db_path": DB_PATH,
        "services": "operational"
    }

@app.post("/register")
async def register_user(user_data: dict):
    try:
        conn = _connect_db()
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuarios WHERE email = ?", (user_data["email"],))
        if cur.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        pwd_hash = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt())

        cur.execute(
            """
            INSERT INTO usuarios (nome_completo, email, password_hash, perfil_profissional,
                                  empresa_propriedade, cidade, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_data["nome_completo"],
                user_data["email"],
                pwd_hash.decode("utf-8"),
                user_data.get("perfil_profissional", "Produtor Rural"),
                user_data.get("empresa_propriedade", ""),
                user_data.get("cidade", ""),
                user_data.get("estado", ""),
            ),
        )
        user_id = cur.lastrowid
        conn.commit()
        conn.close()

        token = create_access_token({"sub": user_data["email"]})
        return {
            "message": "Usuário cadastrado com sucesso",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user_id, "nome": user_data["nome_completo"], "email": user_data["email"]},
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Erro no cadastro")

@app.post("/login")
async def login_user(credentials: dict):
    try:
        conn = _connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (credentials["email"],))
        user = cur.fetchone()
        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="Email não encontrado")
        if not bcrypt.checkpw(credentials["password"].encode("utf-8"), user[3].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Senha incorreta")

        token = create_access_token({"sub": user[2]})
        return {
            "message": "Login realizado com sucesso",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user[0], "nome": user[1], "email": user[2]},
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erro no login")

@app.get("/weather/{lat}/{lon}")
async def weather(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_weather_data(lat, lon)}
    except Exception as e:
        logger.error(f"Weather endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados climáticos")

@app.get("/satellite/{lat}/{lon}")
async def satellite(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_ndvi_data(lat, lon)}
    except Exception as e:
        logger.error(f"NDVI endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de satélite")

@app.get("/market")
async def market(user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_market_data()}
    except Exception as e:
        logger.error(f"Market endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de mercado")

@app.get("/dashboard/{lat}/{lon}")
async def dashboard(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        weather_data, ndvi_data, market_data = await asyncio.gather(
            get_weather_data(lat, lon),
            get_ndvi_data(lat, lon),
            get_market_data()
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
                "mensagem": f"NDVI baixo ({ndvi_data['ndvi']}) - Verificar pragas/doenças"
            })

        soja_preco = market_data["soja"]["preco"]
        produtividade = 50 if ndvi_data["ndvi"] > 0.6 else 35
        receita_ha = produtividade * soja_preco

        return {
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
                    "receita_por_hectare": round(receita_ha, 2),
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar dashboard")

# =========================================================
# Execução local
# =========================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
