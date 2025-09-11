from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import logging
from datetime import datetime, timedelta
import random
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from python_dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("terrasynapse-enterprise")

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "terrasynapse-enterprise-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "fa5b506b2f5299a6617bc5ac2ccc2f58")

# Inicialização FastAPI
app = FastAPI(title="TerraSynapse Enterprise", version="2.2")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")

# Simulação de banco de dados em memória
users_db = {}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Funções auxiliares
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Simulação de dados sem numpy/pandas
def generate_mock_data():
    """Gera dados simulados sem usar numpy/pandas"""
    return {
        "temperatura": round(random.uniform(20, 40), 2),
        "umidade": round(random.uniform(40, 90), 2),
        "precipitacao": round(random.uniform(0, 50), 2),
        "vento": round(random.uniform(5, 25), 2),
        "pressure": round(random.uniform(1000, 1020), 2),
        "ndvi": round(random.uniform(0.3, 0.8), 3),
        "soil_moisture": round(random.uniform(20, 60), 2),
        "ph_solo": round(random.uniform(6.0, 7.5), 1)
    }

# Rotas de autenticação
@app.post("/register")
async def register(email: str = Form(...), password: str = Form(...)):
    try:
        if email in users_db:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        hashed_password = hash_password(password)
        users_db[email] = {"password": hashed_password}
        logger.info(f"Novo usuário: {email}")
        
        # Criar token
        access_token = create_access_token(data={"sub": email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": email
        }
    except Exception as e:
        logger.error(f"Erro registro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        if email not in users_db:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        if not verify_password(password, users_db[email]["password"]):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        access_token = create_access_token(data={"sub": email})
        logger.info(f"Login: {email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

# Rota principal do dashboard
@app.get("/dashboard/{lat}/{lon}")
async def get_dashboard_data(lat: float, lon: float, current_user: str = Depends(get_current_user)):
    try:
        # Dados meteorológicos
        weather_data = await get_weather_data(lat, lon)
        
        # Dados de mercado
        market_data = await get_market_data()
        
        # Dados simulados
        mock_data = generate_mock_data()
        
        response_data = {
            "weather": weather_data,
            "market": market_data,
            "sensors": mock_data,
            "location": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Dashboard: {lat},{lon} - {weather_data.get('temperature', 'N/A')}°C")
        return response_data
        
    except Exception as e:
        logger.error(f"Erro dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

async def get_weather_data(lat: float, lon: float):
    """Busca dados meteorológicos"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "pt_br"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"OpenWeather: {lat},{lon} - {data['main']['temp']}°C")
                return {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "city": data.get("name", "Localização")
                }
    except Exception as e:
        logger.error(f"Erro OpenWeather: {e}")
        
    # Dados padrão em caso de erro
    return {
        "temperature": 25.0,
        "humidity": 65,
        "pressure": 1013,
        "description": "Dados indisponíveis",
        "wind_speed": 10,
        "city": "Capinópolis"
    }

async def get_market_data():
    """Busca dados de mercado"""
    try:
        # Taxa de câmbio
        exchange_rate = await get_exchange_rate()
        
        # Preços simulados (Yahoo Finance está com problema de autenticação)
        commodities = {
            "soja": {"price": round(random.uniform(1400, 1600), 2), "change": round(random.uniform(-5, 5), 2)},
            "milho": {"price": round(random.uniform(600, 800), 2), "change": round(random.uniform(-3, 3), 2)},
            "cafe": {"price": round(random.uniform(1200, 1400), 2), "change": round(random.uniform(-4, 4), 2)}
        }
        
        return {
            "exchange_rate": exchange_rate,
            "commodities": commodities
        }
    except Exception as e:
        logger.error(f"Erro dados mercado: {e}")
        return {
            "exchange_rate": 5.20,
            "commodities": {
                "soja": {"price": 1500.00, "change": 0.5},
                "milho": {"price": 700.00, "change": -0.2},
                "cafe": {"price": 1300.00, "change": 1.2}
            }
        }

async def get_exchange_rate():
    """Busca taxa de câmbio USD/BRL"""
    try:
        url = "https://api.exchangerate.host/latest"
        params = {"base": "USD", "symbols": "BRL"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data["rates"]["BRL"]
    except Exception as e:
        logger.error(f"Erro câmbio: {e}")
    
    return 5.20  # Valor padrão

# Rota de saúde
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Rota raiz
@app.get("/")
async def root():
    return {"message": "TerraSynapse Enterprise API", "version": "2.2", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
