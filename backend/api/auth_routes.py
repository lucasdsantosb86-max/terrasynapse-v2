# backend/api/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from services.auth_service import auth_service, UserRegistration, User

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileInfo(BaseModel):
    """Informações dos perfis profissionais"""
    perfil: str
    nome: str
    descricao: str
    campos_obrigatorios: list
    exemplo_uso: str

@router.get("/profiles", response_model=list[ProfileInfo])
async def get_available_profiles():
    """Listar perfis profissionais disponíveis"""
    profiles = [
        {
            "perfil": "agronomo",
            "nome": "Engenheiro Agrônomo",
            "descricao": "Profissional especializado em culturas vegetais e sistemas produtivos",
            "campos_obrigatorios": ["crea_crmv", "especializacao"],
            "exemplo_uso": "Monitoramento de lavouras, análise de solo, controle fitossanitário"
        },
        {
            "perfil": "zootecnista",
            "nome": "Zootecnista",
            "descricao": "Especialista em produção animal e manejo de rebanhos",
            "campos_obrigatorios": ["crea_crmv", "especializacao"],
            "exemplo_uso": "Gestão de pastagens, nutrição animal, controle reprodutivo"
        },
        {
            "perfil": "fazendeiro_corte",
            "nome": "Pecuarista de Corte",
            "descricao": "Produtor focado na criação de gado para abate",
            "campos_obrigatorios": ["area_atuacao_hectares"],
            "exemplo_uso": "Controle de peso, índices zootécnicos, preços de mercado"
        },
        {
            "perfil": "fazendeiro_leite",
            "nome": "Pecuarista Leiteiro",
            "descricao": "Produtor especializado em produção de leite",
            "campos_obrigatorios": ["area_atuacao_hectares"],
            "exemplo_uso": "Controle de ordenha, qualidade do leite, eficiência reprodutiva"
        },
        {
            "perfil": "gestor_agronegocio",
            "nome": "Gestor do Agronegócio",
            "descricao": "Profissional em gestão de empresas rurais",
            "campos_obrigatorios": ["experiencia_anos"],
            "exemplo_uso": "Análises financeiras, KPIs operacionais, planejamento estratégico"
        },
        {
            "perfil": "genetica_animal",
            "nome": "Especialista em Genética Animal",
            "descricao": "Profissional em melhoramento genético animal",
            "campos_obrigatorios": ["crea_crmv", "especializacao"],
            "exemplo_uso": "Controle genealógico, DEPs, planejamento de acasalamentos"
        },
        {
            "perfil": "genetica_vegetal",
            "nome": "Especialista em Genética Vegetal",
            "descricao": "Profissional em melhoramento genético vegetal",
            "campos_obrigatorios": ["crea_crmv", "especializacao"],
            "exemplo_uso": "Desenvolvimento de cultivares, análises moleculares"
        },
        {
            "perfil": "proprietario_haras",
            "nome": "Proprietário de Haras",
            "descricao": "Criador especializado em equinocultura",
            "campos_obrigatorios": ["area_atuacao_hectares"],
            "exemplo_uso": "Gestão de éguas, controle reprodutivo, treinamentos"
        },
        {
            "perfil": "cooperativa",
            "nome": "Representante de Cooperativa",
            "descricao": "Profissional de cooperativas agropecuárias",
            "campos_obrigatorios": ["experiencia_anos"],
            "exemplo_uso": "Assistência técnica, análise regional, suporte aos cooperados"
        },
        {
            "perfil": "consultor_tecnico",
            "nome": "Consultor Técnico",
            "descricao": "Consultor independente em agropecuária",
            "campos_obrigatorios": ["crea_crmv", "especializacao", "experiencia_anos"],
            "exemplo_uso": "Consultoria especializada, laudos técnicos, projetos"
        }
    ]
    
    return profiles

@router.post("/register")
async def register_user(registration: UserRegistration):
    """Cadastrar novo usuário"""
    try:
        result = await auth_service.register_user(registration)
        return {
            "message": "Usuário cadastrado com sucesso",
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "user": result["user"],
            "dashboard_config": result["perfil_dashboard"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/login")
async def login(login_data: LoginRequest):
    """Login do usuário"""
    try:
        result = await auth_service.login(login_data.email, login_data.password)
        return {
            "message": "Login realizado com sucesso",
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "user": result["user"],
            "dashboard_config": result["perfil_dashboard"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no login: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(auth_service.get_current_user)):
    """Obter informações do usuário atual"""
    return current_user

@router.get("/dashboard-config")
async def get_user_dashboard_config(current_user: User = Depends(auth_service.get_current_user)):
    """Obter configuração do dashboard do usuário"""
    config = auth_service.get_dashboard_config(current_user.perfil_profissional)
    return {
        "user": current_user,
        "dashboard": config
    }

@router.post("/logout")
async def logout(current_user: User = Depends(auth_service.get_current_user)):
    """Logout do usuário"""
    return {"message": "Logout realizado com sucesso"}

@router.get("/validate-token")
async def validate_token(current_user: User = Depends(auth_service.get_current_user)):
    """Validar se token ainda é válido"""
    return {
        "valid": True,
        "user": current_user,
        "dashboard_config": auth_service.get_dashboard_config(current_user.perfil_profissional)
    }