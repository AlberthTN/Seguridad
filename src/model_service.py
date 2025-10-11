"""
Servicio para gestionar modelos de IA y sus credenciales.
Verifica la disponibilidad de modelos y maneja las claves API.
"""

import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from .security_model import AIModelProvider, ModelConfig

load_dotenv()


class ModelService:
    """Servicio para gestionar modelos de IA y credenciales."""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.available_models: List[str] = []
        self.token = os.getenv('API_TOKEN', '')
        self._load_models()
    
    def _load_models(self) -> None:
        """Carga las configuraciones de modelos desde las variables de entorno."""
        # Cargar claves API
        api_keys = {
            AIModelProvider.OPENAI: os.getenv('OPENAI_API_KEY'),
            AIModelProvider.ANTHROPIC: os.getenv('ANTHROPIC_API_KEY'),
            AIModelProvider.GOOGLE: os.getenv('GOOGLE_API_KEY'),
            AIModelProvider.MISTRAL: os.getenv('MISTRAL_API_KEY'),
            AIModelProvider.COHERE: os.getenv('COHERE_API_KEY'),
        }
        
        # Cargar modelos disponibles
        available_models_str = os.getenv('AVAILABLE_MODELS', '')
        if available_models_str:
            model_entries = available_models_str.split(',')
            for entry in model_entries:
                if ':' in entry:
                    provider_name, model_name = entry.split(':', 1)
                    provider = AIModelProvider(provider_name.lower())
                    
                    # Verificar si tenemos la clave API para este proveedor
                    api_key = api_keys.get(provider)
                    is_available = api_key is not None and len(api_key) > 10
                    
                    config = ModelConfig(
                        provider=provider,
                        model_name=model_name,
                        api_key=api_key or '',
                        is_available=is_available
                    )
                    
                    model_id = f"{provider}:{model_name}"
                    self.models[model_id] = config
                    if is_available:
                        self.available_models.append(model_id)
    
    def validate_token(self, token: str) -> bool:
        """Valida si el token proporcionado coincide con el token configurado."""
        return token == self.token and len(self.token) == 32
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Obtiene la configuración de un modelo específico."""
        return self.models.get(model_id)
    
    def is_model_available(self, model_id: str) -> bool:
        """Verifica si un modelo está disponible y configurado."""
        config = self.get_model_config(model_id)
        return config is not None and config.is_available if config else False
    
    def get_available_models(self) -> List[str]:
        """Devuelve la lista de modelos disponibles."""
        return self.available_models
    
    def get_model_provider(self, model_id: str) -> Optional[Tuple[AIModelProvider, str]]:
        """Extrae el proveedor y nombre del modelo del ID."""
        if ':' in model_id:
            provider_name, model_name = model_id.split(':', 1)
            try:
                provider = AIModelProvider(provider_name.lower())
                return provider, model_name
            except ValueError:
                return None
        return None
    
    def check_credentials(self, model_id: str) -> Tuple[bool, str]:
        """Verifica las credenciales para un modelo específico."""
        config = self.get_model_config(model_id)
        if not config:
            return False, f"Modelo '{model_id}' no encontrado"
        
        if not config.is_available:
            provider, _ = self.get_model_provider(model_id) or (None, None)
            if provider:
                env_var = f"{provider.upper()}_API_KEY"
                return False, f"Credenciales no configuradas. Configure {env_var} en .env"
            return False, "Credenciales no configuradas"
        
        return True, "Credenciales válidas"


# Instancia global del servicio de modelos
model_service = ModelService()