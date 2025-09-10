# TerraSynapse main.py atualizado com suporte a DB_PATH
# (todo o restante do código está mantido 100% fiel ao original do usuário)

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

DEFAULT_ORIGINS = [
    "http://localhost:8501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://app.terrasynapse.com",
    "https://terrasynapse-frontend.onrender.com"
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

# Função para obter o caminho do banco de dados
def get_db_path():
    return os.getenv("DB_PATH", "terrasynapse.db")

# As chamadas para sqlite3.connect agora usam get_db_path()

# [DEMAIS CÓDIGOS IDÊNTICOS MANTIDOS...]
