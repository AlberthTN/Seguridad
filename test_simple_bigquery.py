#!/usr/bin/env python3
"""
Script simple para probar inserción directa en BigQuery.
"""

import os
import json
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_direct_insert():
    """Prueba inserción directa en BigQuery."""
    
    # Configurar credenciales
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
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
    
    # Referencia a la tabla
    table_id = f"{project_id}.{dataset_id}.metricas_tools"
    table = client.get_table(table_id)
    
    print("Esquema de la tabla:")
    for field in table.schema:
        print(f"  - {field.name}: {field.field_type} ({field.mode})")
    
    # Datos de prueba usando los nombres exactos del esquema
    test_data = {
        "Id Slack": "TEST0002",
        "Nombre Usuario": "Juan Perez Test",
        "Area Usuario": "Uso Interno",
        "Fecha": datetime.now().isoformat(),
        "Nombre Agente": "A-Seguridad",
        "Input Usuario": "Prueba de inserción directa",
        "Velocidad de Respuesta": 2.5,
        "Tokens Ejecucion": 200,
        "Satisfaccion": 1
    }
    
    print(f"\nInsertando datos: {test_data}")
    
    errors = client.insert_rows_json(table, [test_data])
    
    if errors:
        print(f"✗ Error: {errors}")
        return False
    else:
        print("✓ Inserción exitosa")
        return True

if __name__ == "__main__":
    test_direct_insert()