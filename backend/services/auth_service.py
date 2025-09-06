# backend/services/auth_service.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt
import uuid

# Configuração JWT
SECRET_KEY = "terrasynapse_2024_secure_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class UserProfile(BaseModel):
    """Perfis profissionais disponíveis"""
    AGRONOMO = "agronomo"
    ZOOTECNISTA = "zootecnista"
    FAZENDEIRO_CORTE = "fazendeiro_corte"
    FAZENDEIRO_LEITE = "fazendeiro_leite"
    GESTOR_AGRONEGOCIO = "gestor_agronegocio"
    GENETICA_ANIMAL = "genetica_animal"
    GENETICA_VEGETAL = "genetica_vegetal"
    PROPRIETARIO_HARAS = "proprietario_haras"
    COOPERATIVA = "cooperativa"
    CONSULTOR_TECNICO = "consultor_tecnico"

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    nome_completo: str
    perfil_profissional: str
    cpf_cnpj: str
    telefone: str
    crea_crmv: Optional[str] = None
    empresa_propriedade: str
    cidade: str
    estado: str
    area_atuacao_hectares: Optional[float] = None
    especializacao: Optional[str] = None
    experiencia_anos: Optional[int] = None

class User(BaseModel):
    id: str
    email: str
    nome_completo: str
    perfil_profissional: str
    empresa_propriedade: str
    cidade: str
    estado: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthService:
    def __init__(self):
        # Simulação de banco - substituir por PostgreSQL
        self.users_db = {}
        self.sessions_db = {}

    def hash_password(self, password: str) -> str:
        """Hash seguro da senha"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar senha"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_access_token(self, data: dict) -> str:
        """Criar JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def validate_profile_data(self, registration: UserRegistration) -> bool:
        """Validar dados específicos por perfil"""
        profile_requirements = {
            UserProfile.AGRONOMO: ["crea_crmv"],
            UserProfile.ZOOTECNISTA: ["crea_crmv"],
            UserProfile.GENETICA_ANIMAL: ["crea_crmv"],
            UserProfile.GENETICA_VEGETAL: ["crea_crmv"],
        }
        
        required_fields = profile_requirements.get(registration.perfil_profissional, [])
        
        for field in required_fields:
            if not getattr(registration, field):
                return False
        return True

    async def register_user(self, registration: UserRegistration) -> dict:
        """Registrar novo usuário"""
        
        # Verificar se email já existe
        for user in self.users_db.values():
            if user["email"] == registration.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )

        # Validar dados específicos do perfil
        if not self.validate_profile_data(registration):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dados obrigatórios faltando para perfil {registration.perfil_profissional}"
            )

        # Criar usuário
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(registration.password)
        
        user_data = {
            "id": user_id,
            "email": registration.email,
            "password": hashed_password,
            "nome_completo": registration.nome_completo,
            "perfil_profissional": registration.perfil_profissional,
            "cpf_cnpj": registration.cpf_cnpj,
            "telefone": registration.telefone,
            "crea_crmv": registration.crea_crmv,
            "empresa_propriedade": registration.empresa_propriedade,
            "cidade": registration.cidade,
            "estado": registration.estado,
            "area_atuacao_hectares": registration.area_atuacao_hectares,
            "especializacao": registration.especializacao,
            "experiencia_anos": registration.experiencia_anos,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        self.users_db[user_id] = user_data
        
        # Criar token de acesso
        access_token = self.create_access_token(
            data={"sub": user_id, "perfil": registration.perfil_profissional}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": User(**user_data),
            "perfil_dashboard": self.get_dashboard_config(registration.perfil_profissional)
        }

    async def login(self, email: str, password: str) -> dict:
        """Login do usuário"""
        user = None
        for user_data in self.users_db.values():
            if user_data["email"] == email:
                user = user_data
                break
        
        if not user or not self.verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Conta desativada"
            )
        
        # Atualizar último login
        user["last_login"] = datetime.utcnow()
        
        # Criar token
        access_token = self.create_access_token(
            data={"sub": user["id"], "perfil": user["perfil_profissional"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": User(**user),
            "perfil_dashboard": self.get_dashboard_config(user["perfil_profissional"])
        }

    def get_dashboard_config(self, perfil: str) -> dict:
        """Configuração do dashboard por perfil"""
        configs = {
            UserProfile.AGRONOMO: {
                "titulo": "Dashboard Agronômico",
                "modulos": ["clima", "solo", "pragas", "irrigacao", "ndvi"],
                "cor_tema": "#2E7D32",
                "widgets": ["alertas_fitossanitarios", "calendario_aplicacoes", "analise_solo"]
            },
            UserProfile.ZOOTECNISTA: {
                "titulo": "Dashboard Zootécnico",
                "modulos": ["pastagem", "nutricao", "reproducao", "sanidade"],
                "cor_tema": "#1976D2",
                "widgets": ["indice_pastagem", "controle_reproducao", "alertas_sanitarios"]
            },
            UserProfile.FAZENDEIRO_CORTE: {
                "titulo": "Dashboard Pecuária de Corte",
                "modulos": ["rebanho", "pastagem", "mercado", "financeiro"],
                "cor_tema": "#F57C00",
                "widgets": ["preco_arroba", "indice_pastagem", "controle_peso"]
            },
            UserProfile.FAZENDEIRO_LEITE: {
                "titulo": "Dashboard Pecuária Leiteira",
                "modulos": ["ordenha", "nutricao", "reproducao", "qualidade_leite"],
                "cor_tema": "#0288D1",
                "widgets": ["producao_diaria", "ccs_cbt", "eficiencia_reproducao"]
            },
            UserProfile.GENETICA_ANIMAL: {
                "titulo": "Dashboard Genética Animal",
                "modulos": ["genealogia", "desempenho", "acasalamentos", "dea"],
                "cor_tema": "#7B1FA2",
                "widgets": ["arvore_genealogica", "dep", "controle_acasalamento"]
            },
            UserProfile.PROPRIETARIO_HARAS: {
                "titulo": "Dashboard Equinocultura",
                "modulos": ["cavalos", "reproducao", "treinamento", "competicoes"],
                "cor_tema": "#8D6E63",
                "widgets": ["controle_éguas", "agenda_cobertura", "resultados_competicao"]
            }
        }
        
        return configs.get(perfil, {
            "titulo": "Dashboard Agronegócio",
            "modulos": ["geral"],
            "cor_tema": "#388E3C",
            "widgets": ["dashboard_geral"]
        })

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Obter usuário atual do token"""
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Token inválido")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = self.users_db.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        return User(**user)

# Instância global do serviço
auth_service = AuthService()