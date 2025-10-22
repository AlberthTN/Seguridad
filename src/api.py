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
import time
import tiktoken

from security_model import AnalysisRequest, APIResponse, SecurityResult
from model_service import model_service
from ai_analyzer import ai_analyzer
from bigquery_service import bigquery_service

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


def calculate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Calcula el número aproximado de tokens para un texto dado.
    
    Args:
        text: Texto a analizar
        model: Modelo para el cual calcular tokens
        
    Returns:
        Número aproximado de tokens
    """
    try:
        # Usar tiktoken para calcular tokens de manera más precisa
        if "gpt" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            # Para otros modelos, usar una aproximación
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    except Exception:
        # Fallback: aproximación simple (1 token ≈ 4 caracteres)
        return len(text) // 4


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
    start_time = time.time()
    success = False
    result = None
    
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
        
        # Calcular tokens de entrada
        input_tokens = calculate_tokens(request.text, request.model)
        
        # Realizar análisis con el modelo de IA
        result = await ai_analyzer.analyze_with_ai(request.text, request.model, request.agent)
        
        # Calcular tokens de salida (aproximación basada en la respuesta)
        output_text = str(result.to_json()) if result else ""
        output_tokens = calculate_tokens(output_text, request.model)
        
        success = True
        response = APIResponse(
            success=True,
            data=result.to_json(),
            model_used=request.model
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Registrar métricas en BigQuery
        end_time = time.time()
        response_time = end_time - start_time
        
        # Calcular tokens si no se hizo antes (en caso de error)
        if 'input_tokens' not in locals():
            input_tokens = calculate_tokens(request.text, request.model)
        if 'output_tokens' not in locals():
            output_tokens = 0
        
        # Insertar métrica en BigQuery
        bigquery_service.insert_interaction_metric(
            agent_name=request.agent,
            user_input=request.text,
            response_time=response_time,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success=success
        )


@app.post("/analyze/batch", response_model=APIResponse)
async def analyze_batch_security(
    requests: List[AnalysisRequest],
    _: str = Depends(validate_token)
):
    """Analiza múltiples solicitudes en lote."""
    start_time = time.time()
    success = False
    
    try:
        results = []
        total_input_tokens = 0
        total_output_tokens = 0
        
        for request in requests:
            request_start_time = time.time()
            request_success = False
            
            try:
                # Validar cada modelo individualmente
                is_available, message = model_service.check_credentials(request.model)
                if not is_available:
                    results.append({
                        "success": False,
                        "error": message,
                        "model_used": request.model,
                        "text": request.text[:100] + "..." if len(request.text) > 100 else request.text
                    })
                    
                    # Registrar métrica individual para solicitud fallida
                    request_end_time = time.time()
                    request_response_time = request_end_time - request_start_time
                    input_tokens = calculate_tokens(request.text, request.model)
                    
                    bigquery_service.insert_interaction_metric(
                        agent_name=request.agent,
                        user_input=request.text,
                        response_time=request_response_time,
                        input_tokens=input_tokens,
                        output_tokens=0,
                        success=False
                    )
                    continue
                
                # Calcular tokens de entrada
                input_tokens = calculate_tokens(request.text, request.model)
                total_input_tokens += input_tokens
                
                # Analizar cada solicitud
                result = await ai_analyzer.analyze_with_ai(request.text, request.model, request.agent)
                
                # Calcular tokens de salida
                output_text = str(result.to_json()) if result else ""
                output_tokens = calculate_tokens(output_text, request.model)
                total_output_tokens += output_tokens
                
                results.append({
                    "success": True,
                    "data": result.to_json(),
                    "model_used": request.model
                })
                
                request_success = True
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "model_used": request.model,
                    "text": request.text[:100] + "..." if len(request.text) > 100 else request.text
                })
                
                # En caso de error, calcular solo tokens de entrada
                if 'input_tokens' not in locals():
                    input_tokens = calculate_tokens(request.text, request.model)
                if 'output_tokens' not in locals():
                    output_tokens = 0
            
            finally:
                # Registrar métrica individual para cada solicitud
                request_end_time = time.time()
                request_response_time = request_end_time - request_start_time
                
                bigquery_service.insert_interaction_metric(
                    agent_name=request.agent,
                    user_input=request.text,
                    response_time=request_response_time,
                    input_tokens=input_tokens if 'input_tokens' in locals() else calculate_tokens(request.text, request.model),
                    output_tokens=output_tokens if 'output_tokens' in locals() else 0,
                    success=request_success
                )
        
        success = True
        return APIResponse(
            success=True,
            data={"results": results}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en procesamiento por lotes: {str(e)}"
        )


@app.get("/health/bigquery", response_model=APIResponse)
async def health_bigquery():
    """Verifica el estado de la conexión con BigQuery."""
    try:
        connection_status = bigquery_service.test_connection()
        return APIResponse(
            success=connection_status["status"] == "success",
            data=connection_status
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Error verificando BigQuery: {str(e)}"
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