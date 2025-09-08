from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="TerraSynapse API",
    description="Sistema Profissional Agropecuário",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "TerraSynapse API Online",
        "status": "operational",
        "version": "2.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Endpoints básicos para frontend
@app.post("/auth/login")
async def login(credentials: dict):
    return {
        "message": "Login simulado",
        "user": {
            "nome_completo": credentials.get("email", "Usuario"),
            "perfil_profissional": "agronomo"
        }
    }

@app.get("/api/climate/current")
async def get_climate():
    return {
        "temperature": 24.5,
        "humidity": 68,
        "status": "operational"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
