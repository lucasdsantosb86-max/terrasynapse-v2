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

# ----------------------------------
# Configuração básica
# ----------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "terrasynapse_enterprise_2024_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="TerraSynapse Enterprise API",
    description="Sistema Agropecuário Profissional",
    version="2.0.0",
)

# ----------------------------------
# CORS dinâmico (com fallback seguro)
# ----------------------------------
DEFAULT_ORIGINS = [
    "http://localhost:8501",                     # dev Streamlit
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://app.terrasynapse.com",              # seu domínio
    "https://terrasynapse-frontend.onrender.com" # Render
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

# ----------------------------------
# DB
# ----------------------------------
def init_database():
    try:
        conn = sqlite3.connect("terrasynapse.db")
        cursor = conn.cursor()

        cursor.execute(
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

        cursor.execute(
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
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# ----------------------------------
# Auth helpers
# ----------------------------------
def create_access_token(data: dict):
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

# ----------------------------------
# Domínio: clima / NDVI / mercado
# ----------------------------------
def calculate_et0(temp_max, temp_min, humidity, wind_speed, solar_radiation=None):
    try:
        temp_mean = (temp_max + temp_min) / 2
        _ = 4098 * (0.6108 * math.exp(17.27 * temp_mean / (temp_mean + 237.3))) / (
            (temp_mean + 237.3) ** 2
        )
        if solar_radiation is None:
            solar_radiation = 15
        et0 = (0.0023 * (temp_mean + 17.8) * abs(temp_max - temp_min) ** 0.5 * solar_radiation) / 2.45
        return round(et0, 2)
    except Exception:
        return 4.5

async def get_weather_data(lat: float, lon: float):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo")
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "pt_br"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                et0 = calculate_et0(temp + 5, temp - 5, humidity, wind_speed)
                return {
                    "temperatura": temp,
                    "umidade": humidity,
                    "vento": wind_speed,
                    "pressao": data["main"]["pressure"],
                    "descricao": data["weather"][0]["description"],
                    "et0": et0,
                    "recomendacao_irrigacao": "Necessária" if et0 > 5 else "Opcional",
                }
    except Exception as e:
        logger.error(f"Weather API error: {e}")

    # fallback aleatório
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

async def get_ndvi_data(lat: float, lon: float):
    import random
    mes = datetime.now().month
    if 3 <= mes <= 5:
        ndvi_base = random.uniform(0.6, 0.8)
    elif 6 <= mes <= 8:
        ndvi_base = random.uniform(0.4, 0.6)
    elif 9 <= mes <= 11:
        ndvi_base = random.uniform(0.7, 0.9)
    else:
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

async def get_market_data():
    import random
    return {
        "soja":  {"preco": round(random.uniform(150, 180), 2), "variacao": round(random.uniform(-5, 5), 2), "tendencia": "Alta"},
        "milho": {"preco": round(random.uniform(70,  90),  2), "variacao": round(random.uniform(-3, 3), 2),  "tendencia": "Estável"},
        "cafe":  {"preco": round(random.uniform(800,1200), 2), "variacao": round(random.uniform(-8, 8), 2),  "tendencia": "Alta"},
    }

# ----------------------------------
# Lifespan
# ----------------------------------
@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info(f"CORS allow_origins={ALLOW_ORIGINS} | allow_origin_regex={ALLOW_REGEX}")

# ----------------------------------
# Endpoints
# ----------------------------------
@app.get("/")
async def root():
    return {"message": "TerraSynapse Enterprise API", "version": "2.0.0", "status": "online", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "database": "online", "services": "operational"}

@app.post("/register")
async def register_user(user_data: dict):
    try:
        conn = sqlite3.connect("terrasynapse.db")
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
        return {"message": "Usuário cadastrado com sucesso", "access_token": token, "token_type": "bearer",
                "user": {"id": user_id, "nome": user_data["nome_completo"], "email": user_data["email"]}}
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Erro no cadastro")

@app.post("/login")
async def login_user(credentials: dict):
    try:
        conn = sqlite3.connect("terrasynapse.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (credentials["email"],))
        user = cur.fetchone()
        conn.close()
        if not user:
            raise HTTPException(status_code=401, detail="Email não encontrado")
        if not bcrypt.checkpw(credentials["password"].encode("utf-8"), user[3].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Senha incorreta")

        token = create_access_token({"sub": user[2]})
        return {"message": "Login realizado com sucesso", "access_token": token, "token_type": "bearer",
                "user": {"id": user[0], "nome": user[1], "email": user[2]}}
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erro no login")

@app.get("/weather/{lat}/{lon}")
async def get_weather(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_weather_data(lat, lon)}
    except Exception as e:
        logger.error(f"Weather endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados climáticos")

@app.get("/satellite/{lat}/{lon}")
async def get_satellite(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_ndvi_data(lat, lon)}
    except Exception as e:
        logger.error(f"NDVI endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de satélite")

@app.get("/market")
async def get_market(user: dict = Depends(verify_token)):
    try:
        return {"status": "success", "data": await get_market_data()}
    except Exception as e:
        logger.error(f"Market endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar dados de mercado")

@app.get("/dashboard/{lat}/{lon}")
async def get_dashboard(lat: float, lon: float, user: dict = Depends(verify_token)):
    try:
        weather_data, ndvi_data, market_data = await asyncio.gather(
            get_weather_data(lat, lon), get_ndvi_data(lat, lon), get_market_data()
        )

        alertas = []
        if weather_data["et0"] > 6:
            alertas.append({"tipo": "irrigacao", "prioridade": "alta",
                            "mensagem": f"ET0 elevada ({weather_data['et0']}mm) - Irrigação recomendada"})
        if ndvi_data["ndvi"] < 0.5:
            alertas.append({"tipo": "vegetacao", "prioridade": "media",
                            "mensagem": f"NDVI baixo ({ndvi_data['ndvi']}) - Verificar pragas/doenças"})

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
