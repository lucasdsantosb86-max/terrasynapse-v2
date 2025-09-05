from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="TerraSynapse API",
    description="Sistema de Monitoramento Agrícola - Backend",
    version="2.0.0"
)

# CORS para permitir frontend
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
        "message": "TerraSynapse V2.0 API - Sistema Online",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "2.0.0",
        "service": "TerraSynapse Backend"
    }

@app.get("/api/weather")
async def get_weather():
    return {
        "temperature": 25.5,
        "humidity": 68,
        "wind_speed": 15,
        "status": "demo_mode"
    }

@app.get("/api/satellite")
async def get_satellite():
    return {
        "ndvi": 0.75,
        "coordinates": [-19.0919, -50.2991],
        "status": "demo_mode"
    }

@app.get("/api/market")
async def get_market():
    return {
        "soja": 155.50,
        "milho": 48.30,
        "variacao": 2.1,
        "status": "demo_mode"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)