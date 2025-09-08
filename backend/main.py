from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3
import bcrypt
import jwt
import uvicorn
from api.routes import router as api_router
app.include_router(api_router)
from datetime import datetime, timedelta
import os

# Configuração JWT
SECRET_KEY = "terrasynapse_production_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="TerraSynapse Enterprise API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

security = HTTPBearer()

class UserRegister(BaseModel):
    nome_completo: str
    email: str
    password: str
    perfil_profissional: str
    empresa_propriedade: str
    cidade: str
    estado: str

class UserLogin(BaseModel):
    email: str
    password: str

class DatabaseManager:
    def __init__(self):
        self.db_path = "terrasynapse.db"
        self.init_database()
        self.create_admin_user()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                perfil_profissional TEXT NOT NULL,
                empresa_propriedade TEXT NOT NULL,
                cidade TEXT NOT NULL,
                estado TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        conn.commit()
        conn.close()

    def create_admin_user(self):
        # Criar usuário admin padrão
        admin_data = {
            "nome_completo": "Lucas dos Santos Batista",
            "email": "terrasynapse@terrasynapse.com",
            "password": "Luc084as688",
            "perfil_profissional": "engenheiro_agronomo",
            "empresa_propriedade": "TerraSynapse",
            "cidade": "Capinópolis",
            "estado": "MG"
        }
        
        if not self.get_user_by_email(admin_data["email"]):
            self.create_user(admin_data)

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))

    def create_user(self, user_data: dict) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(user_data["password"])
            
            cursor.execute('''
                INSERT INTO users (nome_completo, email, password_hash, perfil_profissional, 
                                 empresa_propriedade, cidade, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data["nome_completo"],
                user_data["email"], 
                password_hash,
                user_data["perfil_profissional"],
                user_data["empresa_propriedade"],
                user_data["cidade"],
                user_data["estado"]
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_email(self, email: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = TRUE', (email,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.get_user_by_email(email)
        if user and self.verify_password(password, user["password_hash"]):
            return user
        return None

db = DatabaseManager()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return db.get_user_by_email(email)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.post("/auth/register")
async def register(user: UserRegister):
    user_dict = user.dict()
    if db.create_user(user_dict):
        return {"message": "Usuário criado com sucesso"}
    else:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

@app.post("/auth/login")
async def login(credentials: UserLogin):
    user = db.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "nome_completo": user["nome_completo"],
            "email": user["email"],
            "perfil_profissional": user["perfil_profissional"],
            "empresa_propriedade": user["empresa_propriedade"],
            "cidade": user["cidade"],
            "estado": user["estado"]
        }
    }

@app.get("/auth/me")
async def get_current_user(user: dict = Depends(verify_token)):
    return {
        "nome_completo": user["nome_completo"],
        "email": user["email"],
        "perfil_profissional": user["perfil_profissional"],
        "empresa_propriedade": user["empresa_propriedade"],
        "cidade": user["cidade"],
        "estado": user["estado"]
    }

@app.get("/")
async def root():
    return {"message": "TerraSynapse Enterprise API", "status": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
