"""
Servicio para gestionar modelos de IA y sus credenciales.
Verifica la disponibilidad de modelos y maneja las claves API.
"""

import os
from typing import Dict, List, Optional, Tuple
from security_model import AIModelProvider, ModelConfig

# Usar únicamente variables de entorno del sistema (Portainer/Docker)
print("DEBUG: Usando variables de entorno del sistema (Portainer/Docker)")


class ModelService:
    """Servicio para gestionar modelos de IA y credenciales."""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.available_models: List[str] = []
        self.token = os.getenv('API_TOKEN', '')
        print(f"DEBUG: API_TOKEN cargado: {'✓' if self.token else '✗'} (longitud: {len(self.token)})")
        self._load_models()
    
    def _load_models(self) -> None:
        """Carga las configuraciones de modelos desde las variables de entorno."""
        print("DEBUG: Iniciando carga de modelos...")
        
        # Debug detallado de todas las variables de entorno relevantes
        print("DEBUG: === VARIABLES DE ENTORNO ===")
        env_vars = ['API_TOKEN', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 
                   'MISTRAL_API_KEY', 'COHERE_API_KEY', 'AVAILABLE_MODELS']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                length = len(value)
                masked_value = value[:10] + "..." if length > 10 else value
                print(f"DEBUG: {var} = {masked_value} (longitud: {length})")
            else:
                print(f"DEBUG: {var} = NO CONFIGURADA")
        print("DEBUG: === FIN VARIABLES DE ENTORNO ===")
        
        # Cargar claves API
        api_keys = {
            AIModelProvider.OPENAI: os.getenv('OPENAI_API_KEY'),
            AIModelProvider.ANTHROPIC: os.getenv('ANTHROPIC_API_KEY'),
            AIModelProvider.GOOGLE: os.getenv('GOOGLE_API_KEY'),
            AIModelProvider.MISTRAL: os.getenv('MISTRAL_API_KEY'),
            AIModelProvider.COHERE: os.getenv('COHERE_API_KEY'),
        }
        
        # Debug de API keys
        for provider, key in api_keys.items():
            status = "✓" if key and len(key) > 10 else "✗"
            length = len(key) if key else 0
            print(f"DEBUG: {provider.value.upper()}_API_KEY: {status} (longitud: {length})")
        
        # Cargar modelos disponibles desde variables de entorno
        available_models_str = os.getenv('AVAILABLE_MODELS', '')
        print(f"DEBUG: AVAILABLE_MODELS encontrado: {'✓' if available_models_str else '✗'}")
        print(f"DEBUG: AVAILABLE_MODELS valor: {available_models_str}")
        
        # Si no hay AVAILABLE_MODELS en variables de entorno, usar lista predefinida
        if not available_models_str:
            print("DEBUG: AVAILABLE_MODELS vacío, usando lista predefinida")
            available_models_str = "openai:gpt-4o,openai:gpt-4o-mini,openai:gpt-4-turbo,openai:gpt-4,openai:gpt-3.5-turbo,anthropic:claude-3-5-sonnet-20241022,anthropic:claude-3-5-haiku-20241022,anthropic:claude-3-opus-20240229,anthropic:claude-3-sonnet-20240229,anthropic:claude-3-haiku-20240307,google:gemini-2.0-flash-exp,google:gemini-1.5-pro,google:gemini-1.5-flash,google:gemini-1.0-pro,mistral:mistral-large-latest,mistral:mistral-medium-latest,mistral:mistral-small-latest,mistral:codestral-latest,cohere:command-a-03-2025,cohere:command-r7b-12-2024,cohere:command-r-08-2024,cohere:command-r-plus-08-2024"
        
        if available_models_str:
            model_entries = available_models_str.split(',')
            print(f"DEBUG: Procesando {len(model_entries)} modelos")
            
            for entry in model_entries:
                entry = entry.strip()  # Limpiar espacios
                if ':' in entry:
                    provider_name, model_name = entry.split(':', 1)
                    try:
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
                        
                        model_id = f"{provider.value}:{model_name}"
                        self.models[model_id] = config
                        # Mostrar todos los modelos configurados (incluso sin API keys para debug)
                        self.available_models.append(model_id)
                        
                        print(f"DEBUG: Modelo registrado - {model_id}, Disponible: {is_available}")
                        
                    except ValueError as e:
                        print(f"DEBUG: Error con proveedor '{provider_name}': {e}")
                        continue
                else:
                    print(f"DEBUG: Formato inválido para modelo: {entry}")
        
        print(f"DEBUG: Total modelos cargados: {len(self.models)}")
        print(f"DEBUG: Modelos disponibles: {self.available_models}")
    
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
                env_var = f"{provider.value.upper()}_API_KEY"
                return False, f"Credenciales no configuradas. Configure {env_var} en variables de entorno"
            return False, "Credenciales no configuradas"
        
        return True, "Credenciales válidas"


# Instancia global del servicio de modelos
model_service = ModelService()