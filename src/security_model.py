from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum
import re


class SecurityRequest(BaseModel):
    input: str = Field(..., description="Texto de la solicitud del usuario a analizar")


class SecurityResult(BaseModel):
    is_safe: bool = Field(..., description="True si la solicitud es segura, False si no lo es")
    score: float = Field(..., ge=0.0, le=1.0, description="Puntaje de riesgo agregado entre 0 y 1")
    category_scores: Dict[str, float] = Field(default_factory=dict, description="Puntaje por categoría de riesgo")
    reasons: List[str] = Field(default_factory=list, description="Razones detectadas que justifican el veredicto")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias para mitigar o reformular")
    model_used: str = Field(default="", description="Modelo de IA utilizado para el análisis")

    def to_json(self) -> Dict:
        """Devuelve el resultado como dict listo para serializar a JSON."""
        return self.model_dump()


class AIModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Texto a analizar")
    model: str = Field(..., description="Modelo a usar (formato: proveedor:modelo)")
    token: str = Field(..., description="Token de autenticación de 32 caracteres hexadecimales")

    @validator('token')
    def validate_token_format(cls, v):
        if not re.match(r'^[a-f0-9]{32}$', v):
            raise ValueError('El token debe tener exactamente 32 caracteres hexadecimales')
        return v

    @validator('model')
    def validate_model_format(cls, v):
        if not re.match(r'^[a-z]+:[a-zA-Z0-9-_.]+$', v):
            raise ValueError('Formato de modelo inválido. Use: proveedor:modelo')
        return v


class APIResponse(BaseModel):
    success: bool = Field(..., description="Indica si la solicitud fue exitosa")
    data: Optional[Dict] = Field(default=None, description="Datos de la respuesta")
    error: Optional[str] = Field(default=None, description="Mensaje de error si hubo fallo")
    model_used: Optional[str] = Field(default=None, description="Modelo de IA utilizado")


class ModelConfig(BaseModel):
    provider: AIModelProvider
    model_name: str
    api_key: str
    is_available: bool = True