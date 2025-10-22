"""
API REST para el Agente de Seguridad con autenticación por token.
Expone endpoints para análisis de seguridad usando modelos de IA.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import uvicorn
import os

from security_model import AnalysisRequest, APIResponse, SecurityResult
from model_service import model_service
from ai_analyzer import ai_analyzer

app = FastAPI(
    title="Agente de Seguridad API",
    description="API REST para análisis de seguridad de solicitudes usando modelos de IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema de autenticación
security = HTTPBearer()


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida el token de autenticación."""
    token = credentials.credentials
    if not model_service.validate_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.get("/", response_model=APIResponse)
async def root():
    """Endpoint raíz con información de la API."""
    return APIResponse(
        success=True,
        data={
            "message": "Agente de Seguridad API",
            "version": "1.0.0",
            "available_models": model_service.get_available_models()
        }
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Endpoint de health check."""
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "available_models": len(model_service.get_available_models()),
            "token_configured": len(model_service.token) == 32
        }
    )


@app.get("/debug/env", response_model=APIResponse)
async def debug_environment(_: str = Depends(validate_token)):
    """Endpoint de debug para verificar variables de entorno."""
    try:
        import os
        env_vars = ['API_TOKEN', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 
                   'MISTRAL_API_KEY', 'COHERE_API_KEY', 'AVAILABLE_MODELS']
        
        env_info = {}
        for var in env_vars:
            value = os.getenv(var)
            if value:
                length = len(value)
                masked_value = value[:10] + "..." if length > 10 else value
                env_info[var] = {
                    "configured": True,
                    "length": length,
                    "masked_value": masked_value
                }
            else:
                env_info[var] = {
                    "configured": False,
                    "length": 0,
                    "masked_value": "NO_CONFIGURADA"
                }
        
        return {
            "success": True,
            "data": {
                "environment_variables": env_info,
                "available_models_raw": os.getenv('AVAILABLE_MODELS', 'NO_CONFIGURADA'),
                "models_loaded": model_service.get_available_models()
            },
            "message": "Información de debug de variables de entorno"
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"Error en debug: {str(e)}"
        }


@app.get("/models", response_model=APIResponse)
async def list_models(_: str = Depends(validate_token)):
    """Lista todos los modelos disponibles con su estado."""
    models_info = []
    for model_id in model_service.models.keys():
        config = model_service.get_model_config(model_id)
        if config:
            models_info.append({
                "model_id": model_id,
                "provider": config.provider.value,
                "available": config.is_available,
                "has_credentials": bool(config.api_key and len(config.api_key) > 10),
                "credentials_status": "configured" if config.api_key and len(config.api_key) > 10 else "missing",
                "api_key_length": len(config.api_key) if config.api_key else 0
            })
    
    # Información de debug para diagnóstico
    debug_info = {
        "env_vars_loaded": bool(os.getenv('AVAILABLE_MODELS')),
        "available_models_env": os.getenv('AVAILABLE_MODELS', 'NOT_SET'),
        "total_models_configured": len(model_service.models),
        "api_keys_configured": {
            "openai": bool(os.getenv('OPENAI_API_KEY')),
            "anthropic": bool(os.getenv('ANTHROPIC_API_KEY')),
            "google": bool(os.getenv('GOOGLE_API_KEY')),
            "mistral": bool(os.getenv('MISTRAL_API_KEY')),
            "cohere": bool(os.getenv('COHERE_API_KEY'))
        }
    }
    
    return APIResponse(
        success=True,
        data={
            "models": models_info,
            "available_models": model_service.get_available_models(),
            "debug": debug_info
        }
    )


@app.post("/analyze", response_model=APIResponse)
async def analyze_security(
    request: AnalysisRequest,
    _: str = Depends(validate_token)
):
    """
    Analiza una solicitud de texto usando el modelo especificado.
    
    Requiere autenticación por token Bearer.
    """
    try:
        # Validar token de autenticación (ya validado por el dependency)
        
        # Validar que el modelo existe y está disponible
        is_available, message = model_service.check_credentials(request.model)
        if not is_available:
            return APIResponse(
                success=False,
                error=message,
                model_used=request.model
            )
        
        # Realizar análisis con el modelo de IA
        result = await ai_analyzer.analyze_with_ai(request.text, request.model)
        
        return APIResponse(
            success=True,
            data=result.to_json(),
            model_used=request.model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/analyze/batch", response_model=APIResponse)
async def analyze_batch_security(
    requests: List[AnalysisRequest],
    _: str = Depends(validate_token)
):
    """Analiza múltiples solicitudes en lote."""
    try:
        results = []
        
        for request in requests:
            # Validar cada modelo individualmente
            is_available, message = model_service.check_credentials(request.model)
            if not is_available:
                results.append({
                    "success": False,
                    "error": message,
                    "model_used": request.model,
                    "text": request.text[:100] + "..." if len(request.text) > 100 else request.text
                })
                continue
            
            # Analizar cada solicitud
            result = await ai_analyzer.analyze_with_ai(request.text, request.model)
            results.append({
                "success": True,
                "data": result.to_json(),
                "model_used": request.model
            })
        
        return APIResponse(
            success=True,
            data={"results": results}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en procesamiento por lotes: {str(e)}"
        )


def run_api():
    """Función para ejecutar la API."""
    port = int(os.getenv('PORT', 1401))
    host = os.getenv('API_HOST', '0.0.0.0')
    reload = os.getenv('API_RELOAD', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando Agente de Seguridad API en http://{host}:{port}")
    print(f"📖 Documentación disponible en http://{host}:{port}/docs")
    print(f"🔐 Token de autenticación: {'Configurado' if len(model_service.token) == 32 else 'NO configurado'}")
    print(f"🤖 Modelos disponibles: {len(model_service.get_available_models())}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    run_api()