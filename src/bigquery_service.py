"""
Servicio para manejar la conexión e inserción de datos en BigQuery.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class BigQueryService:
    """Servicio para manejar operaciones con BigQuery."""
    
    def __init__(self):
        """Inicializa el servicio de BigQuery."""
        print("🔍 INICIANDO SERVICIO BIGQUERY - PRINT DEBUG")
        
        # Debug completo de variables de entorno
        print("=== TODAS LAS VARIABLES DE ENTORNO ===")
        bigquery_vars = [key for key in os.environ.keys() if 'BIGQUERY' in key or 'GOOGLE' in key]
        if bigquery_vars:
            for var in sorted(bigquery_vars):
                value = os.environ[var]
                if len(value) > 50:
                    print(f"DEBUG ENV: {var} = {value[:50]}... (longitud: {len(value)})")
                else:
                    print(f"DEBUG ENV: {var} = {value}")
        else:
            print("❌ NO SE ENCONTRARON VARIABLES DE BIGQUERY/GOOGLE EN EL ENTORNO")
        
        # Verificar variables específicas
        self.client = None
        self.project_id = os.getenv('BIGQUERY_PROJECT_ID')
        self.dataset_id = os.getenv('BIGQUERY_DATASET')
        self.location = os.getenv('BIGQUERY_LOCATION', 'us-central1')
        self.max_bytes_billed = int(os.getenv('BIGQUERY_MAX_BYTES_BILLED', '30000000000'))
        
        # Debug de variables de entorno específicas
        print(f"DEBUG: BIGQUERY_PROJECT_ID = {self.project_id}")
        print(f"DEBUG: BIGQUERY_DATASET = {self.dataset_id}")
        print(f"DEBUG: BIGQUERY_LOCATION = {self.location}")
        print(f"DEBUG: BIGQUERY_MAX_BYTES_BILLED = {self.max_bytes_billed}")
        
        # Configurar credenciales
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Configura las credenciales de Google Cloud."""
        try:
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            print(f"DEBUG: GOOGLE_APPLICATION_CREDENTIALS_JSON encontrado: {'✓' if credentials_json else '✗'}")
            
            if credentials_json:
                print(f"DEBUG: Longitud de credenciales JSON: {len(credentials_json)}")
                print(f"DEBUG: Primeros 100 caracteres: {credentials_json[:100]}...")
                
                # Parsear las credenciales desde la variable de entorno
                credentials_info = json.loads(credentials_json)
                print(f"DEBUG: JSON parseado correctamente, project_id: {credentials_info.get('project_id', 'NO ENCONTRADO')}")
                
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/bigquery']
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id,
                    location=self.location
                )
                print("✅ Cliente BigQuery configurado correctamente")
            else:
                print("❌ No se encontraron credenciales de Google Cloud")
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de credenciales: {e}")
            self.client = None
        except Exception as e:
            print(f"❌ Error configurando credenciales BigQuery: {e}")
            self.client = None
    
    def is_configured(self) -> bool:
        """Verifica si BigQuery está configurado correctamente."""
        return self.client is not None and self.project_id and self.dataset_id
    
    def insert_interaction_metric(
        self,
        agent_name: str,
        user_input: str,
        response_time: float,
        input_tokens: int,
        output_tokens: int,
        success: bool,
        user_id: str = "ADS0000",
        user_name: str = "A-Seguridad"
    ) -> bool:
        """
        Inserta una métrica de interacción en la tabla de BigQuery.
        
        Args:
            agent_name: Nombre del agente que realizó la consulta
            user_input: Texto de entrada del usuario
            response_time: Tiempo de respuesta en segundos
            input_tokens: Número de tokens de entrada
            output_tokens: Número de tokens de salida
            success: Si la operación fue exitosa
            
        Returns:
            bool: True si la inserción fue exitosa, False en caso contrario
        """
        if not self.is_configured():
            logger.warning("BigQuery no está configurado, saltando inserción de métricas")
            return False
        
        try:
            # Preparar los datos para insertar
            current_time = datetime.now().isoformat()
            total_tokens = input_tokens + output_tokens
            
            row_data = {
                "Id Slack": user_id,
                "Nombre Usuario": agent_name,
                "Area Usuario": "Uso Interno", 
                "Fecha": current_time,
                "Nombre Agente": user_name,
                "Input Usuario": user_input,
                "Velocidad de Respuesta": response_time,
                "Tokens Ejecucion": total_tokens,
                "Satisfaccion": 1 if success else 0
            }
            
            # Referencia a la tabla
            table_id = f"{self.project_id}.{self.dataset_id}.agentes_slack"
            table = self.client.get_table(table_id)
            
            # Insertar la fila
            errors = self.client.insert_rows_json(table, [row_data])
            
            if errors:
                logger.error(f"Error insertando en BigQuery: {errors}")
                return False
            else:
                logger.info(f"Métrica insertada correctamente en BigQuery para agente: {agent_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error insertando métrica en BigQuery: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con BigQuery.
        
        Returns:
            Dict con información sobre el estado de la conexión
        """
        if not self.is_configured():
            return {
                "status": "error",
                "message": "BigQuery no está configurado",
                "configured": False
            }
        
        try:
            # Intentar hacer una consulta simple
            query = f"SELECT 1 as test_connection LIMIT 1"
            job_config = bigquery.QueryJobConfig(
                maximum_bytes_billed=self.max_bytes_billed
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return {
                "status": "success",
                "message": "Conexión exitosa con BigQuery",
                "configured": True,
                "project_id": self.project_id,
                "dataset_id": self.dataset_id,
                "location": self.location
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error conectando con BigQuery: {str(e)}",
                "configured": False
            }

# Instancia global del servicio
bigquery_service = BigQueryService()