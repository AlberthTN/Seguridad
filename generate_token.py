#!/usr/bin/env python3
"""
Script para generar un token seguro de 32 caracteres hexadecimales
para autenticación API y actualizar el archivo .env automáticamente.
"""

import secrets
import re
import os
from pathlib import Path

def generate_secure_token() -> str:
    """Genera un token seguro de 32 caracteres hexadecimales."""
    return secrets.token_hex(16)  # 16 bytes = 32 caracteres hex

def update_env_file(token: str) -> bool:
    """Actualiza el archivo .env con el nuevo token."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Error: No se encontró el archivo .env")
        return False
    
    try:
        # Leer contenido actual
        content = env_path.read_text(encoding='utf-8')
        
        # Reemplazar el token
        if "API_TOKEN=" in content:
            # Buscar y reemplazar la línea del token
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("API_TOKEN="):
                    lines[i] = f"API_TOKEN={token}"
                    break
            content = '\n'.join(lines)
        else:
            # Agregar el token si no existe
            content += f"\nAPI_TOKEN={token}\n"
        
        # Escribir el contenido actualizado
        env_path.write_text(content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar .env: {e}")
        return False

def main():
    """Función principal."""
    print("🔐 Generador de Token Seguro")
    print("=" * 40)
    
    # Generar token
    token = generate_secure_token()
    print(f"✅ Token generado: {token}")
    
    # Verificar formato
    if not re.match(r'^[a-f0-9]{32}$', token):
        print("❌ Error: El token generado no tiene el formato correcto")
        return 1
    
    # Actualizar archivo .env
    if update_env_file(token):
        print("✅ Token actualizado en archivo .env")
        print("\n📋 Para usar el token en las solicitudes API:")
        print(f"   Authorization: Bearer {token}")
        print("\n⚠️  Guarda este token en un lugar seguro!")
        print("   Es necesario para autenticar todas las solicitudes API.")
        return 0
    else:
        print("❌ No se pudo actualizar el archivo .env")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())