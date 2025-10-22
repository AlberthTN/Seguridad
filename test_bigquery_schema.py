#!/usr/bin/env python3
"""
Script para verificar y crear la tabla de BigQuery con el esquema correcto.
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def setup_bigquery_table():
    """Configura la tabla de BigQuery con el esquema correcto."""
    
    # Configurar credenciales
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        print("Error: No se encontraron credenciales de Google Cloud")
        return False
    
    try:
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/bigquery']
        )
        
        project_id = os.getenv('BIGQUERY_PROJECT_ID')
        dataset_id = os.getenv('BIGQUERY_DATASET')
        
        client = bigquery.Client(
            credentials=credentials,
            project=project_id
        )
        
        # Definir el esquema de la tabla
        schema = [
            bigquery.SchemaField("Id_Slack", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Nombre_Usuario", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Area_Usuario", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Fecha", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("Nombre_Agente", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Input_Usuario", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("Velocidad_de_Respuesta", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("Tokens_Ejecucion", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("Satisfaccion", "STRING", mode="REQUIRED"),
        ]
        
        # Referencia a la tabla
        table_id = f"{project_id}.{dataset_id}.agentes_slack"
        
        try:
            # Verificar si la tabla existe
            table = client.get_table(table_id)
            print(f"✓ La tabla {table_id} ya existe")
            
            # Mostrar el esquema actual
            print("\nEsquema actual:")
            for field in table.schema:
                print(f"  - {field.name}: {field.field_type} ({field.mode})")
                
        except Exception as e:
            if "Not found" in str(e):
                # Crear la tabla
                table = bigquery.Table(table_id, schema=schema)
                table = client.create_table(table)
                print(f"✓ Tabla {table_id} creada exitosamente")
                
                print("\nEsquema creado:")
                for field in table.schema:
                    print(f"  - {field.name}: {field.field_type} ({field.mode})")
            else:
                print(f"Error verificando tabla: {e}")
                return False
        
        # Probar inserción de datos de prueba
        test_data = {
            "Id_Slack": "TEST0001",
            "Nombre_Usuario": "Usuario Test",
            "Area_Usuario": "Uso Interno",
            "Fecha": "2025-01-22T16:45:00",
            "Nombre_Agente": "A-Seguridad",
            "Input_Usuario": "Texto de prueba para verificar inserción",
            "Velocidad_de_Respuesta": 1.5,
            "Tokens_Ejecucion": 150,
            "Satisfaccion": "Good"
        }
        
        print(f"\nProbando inserción de datos...")
        errors = client.insert_rows_json(table, [test_data])
        
        if errors:
            print(f"✗ Error en inserción de prueba: {errors}")
            return False
        else:
            print("✓ Inserción de prueba exitosa")
            return True
            
    except Exception as e:
        print(f"Error configurando BigQuery: {e}")
        return False

if __name__ == "__main__":
    print("=== Verificación y configuración de tabla BigQuery ===")
    success = setup_bigquery_table()
    if success:
        print("\n✓ Configuración completada exitosamente")
    else:
        print("\n✗ Error en la configuración")