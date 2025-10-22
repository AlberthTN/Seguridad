#!/usr/bin/env python3
"""
Agente de Seguridad - CLI y Servidor API

Modo CLI: python main.py "texto a analizar"
Modo API: python main.py --api
"""

import json
import sys
import argparse
import asyncio
from typing import Optional, List

from security_model import SecurityRequest, AnalysisRequest
from security_analyzer import analyze_request
from api import run_api
from ai_analyzer import ai_analyzer
from model_service import model_service


def print_help():
    """Muestra la ayuda del programa."""
    print("""
Agente de Seguridad - Análisis de solicitudes con IA

Uso:
  python main.py "texto a analizar"          # Modo CLI básico
  python main.py --api                        # Modo servidor API
  python main.py --analyze-ai "texto" --model openai:gpt-4o  # Modo IA
  python main.py --list-models                # Listar modelos disponibles
  python main.py --check-config               # Verificar configuración

Opciones:
  --api               Iniciar servidor API REST
  --analyze-ai TEXT   Analizar texto con modelo de IA específico
  --model MODEL       Especificar modelo (ej: openai:gpt-4o)
  --list-models       Listar modelos configurados y disponibles
  --check-config      Verificar configuración y credenciales
  --help              Mostrar esta ayuda
""")


def main_cli(text: str) -> int:
    """Modo CLI: análisis básico con motor de reglas."""
    req = SecurityRequest(input=text)
    res = analyze_request(req)
    print(json.dumps(res.to_json(), ensure_ascii=False, indent=2))
    return 0


async def main_ai_analysis(text: str, model_id: str) -> int:
    """Modo IA: análisis con modelos reales de IA."""
    try:
        # Validar modelo
        is_available, message = model_service.check_credentials(model_id)
        if not is_available:
            print(f"❌ Error: {message}")
            return 1
        
        print(f"🔍 Analizando con {model_id}...")
        result = await ai_analyzer.analyze_with_ai(text, model_id)
        
        print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        print(f"❌ Error en análisis con IA: {e}")
        return 1


def list_models() -> int:
    """Listar modelos disponibles."""
    print("\n🤖 Modelos configurados:")
    print("=" * 50)
    
    available_count = 0
    for model_id, config in model_service.models.items():
        status = "✅ DISPONIBLE" if config.is_available else "❌ NO DISPONIBLE"
        cred_status = "🔑 CON CREDENCIALES" if config.api_key else "🚫 SIN CREDENCIALES"
        print(f"{model_id}: {status} | {cred_status}")
        if config.is_available:
            available_count += 1
    
    print(f"\n📊 Total modelos disponibles: {available_count}")
    print(f"🔐 Token API configurado: {'✅ SÍ' if len(model_service.token) == 32 else '❌ NO'}")
    
    if available_count == 0:
        print("\n⚠️  No hay modelos disponibles. Configure las claves API en .env")
        print("   Ejecute 'python main.py --check-config' para más detalles")
    
    return 0


def check_configuration() -> int:
    """Verificar configuración del sistema."""
    print("\n🔧 Verificación de configuración:")
    print("=" * 50)
    
    # Verificar token
    token = model_service.token
    if len(token) == 32:
        print(f"✅ Token API: {token[:8]}...{token[-8:]}")
    else:
        print(f"❌ Token API: No configurado o inválido (debe tener 32 caracteres)")
    
    # Verificar claves API
    providers = {
        'OPENAI_API_KEY': 'OpenAI',
        'ANTHROPIC_API_KEY': 'Anthropic', 
        'GOOGLE_API_KEY': 'Google',
        'MISTRAL_API_KEY': 'Mistral',
        'COHERE_API_KEY': 'Cohere'
    }
    
    print("\n🔑 Credenciales API:")
    for env_var, provider in providers.items():
        key = getattr(model_service, f'_{env_var}', None) or ''
        if key and len(key) > 10:
            print(f"✅ {provider}: Configurado")
        else:
            print(f"❌ {provider}: No configurado")
    
    # Verificar modelos disponibles
    available_models = model_service.get_available_models()
    print(f"\n🤖 Modelos disponibles: {len(available_models)}")
    for model in available_models:
        print(f"  ✅ {model}")
    
    if len(available_models) == 0:
        print("\n⚠️  Configure al menos una clave API en el archivo .env")
        print("   Luego ejecute 'python main.py --list-models'")
    
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Función principal con soporte para múltiples modos."""
    parser = argparse.ArgumentParser(description="Agente de Seguridad con IA", add_help=False)
    parser.add_argument('text', nargs='*', help='Texto a analizar')
    parser.add_argument('--api', action='store_true', help='Iniciar servidor API')
    parser.add_argument('--analyze-ai', metavar='TEXT', help='Analizar texto con IA')
    parser.add_argument('--model', help='Modelo a usar (ej: openai:gpt-4o)')
    parser.add_argument('--list-models', action='store_true', help='Listar modelos disponibles')
    parser.add_argument('--check-config', action='store_true', help='Verificar configuración')
    parser.add_argument('--help', action='store_true', help='Mostrar ayuda')
    
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    
    if args.help:
        print_help()
        return 0
    
    if args.api:
        # Modo servidor API
        run_api()
        return 0
    
    if args.list_models:
        # Listar modelos
        return list_models()
    
    if args.check_config:
        # Verificar configuración
        return check_configuration()
    
    if args.analyze_ai:
        # Modo IA con modelo específico
        if not args.model:
            print("❌ Error: Debe especificar un modelo con --model")
            return 1
        
        return asyncio.run(main_ai_analysis(args.analyze_ai, args.model))
    
    if args.text:
        # Modo CLI básico
        text = " ".join(args.text)
        return main_cli(text)
    else:
        # Modo interactivo o ayuda
        if sys.stdin.isatty():
            print_help()
            return 0
        else:
            # Leer de stdin
            text = sys.stdin.read().strip()
            if text:
                return main_cli(text)
            else:
                print_help()
                return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Ejecución interrumpida")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)