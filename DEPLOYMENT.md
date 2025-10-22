# 🐳 Docker Deployment Guide - Agente de Seguridad

## 📋 Prerrequisitos

1. **Docker Desktop** instalado y ejecutándose
2. **Cuenta en Docker Hub** (para subir la imagen)
3. **Variables de entorno** configuradas

## 🚀 Pasos para Despliegue

### 1. Verificar Docker
```bash
docker --version
docker info
```

### 2. Construir la Imagen Docker
```bash
cd d:\IA\Agentes2025\seguridad
docker build -t alberth121484/seguridad:01.00.002 .
```

**Nota**: La imagen `alberth121484/seguridad:01.00.002` incluye:
- ✅ Integración completa con BigQuery para métricas avanzadas
- ✅ Mejoras en detección de hashes y contenido encriptado
- ✅ Variables de entorno dinámicas optimizadas
- ✅ Debugging mejorado y manejo robusto de errores

### 3. Probar la Imagen Localmente
```bash
docker run -p 1401:1401 -e API_TOKEN="tu_token" alberth121484/seguridad:01.00.002
```

### 4. Iniciar Sesión en Docker Hub
```bash
docker login
# Ingresa tus credenciales de Docker Hub
```

### 5. Subir la Imagen a Docker Hub
```bash
docker push alberth121484/seguridad:01.00.002
```

### 6. Desplegar con Docker Compose
```bash
cd d:\IA\Agentes2025\seguridad
# Crear archivo .env con las variables necesarias
docker-compose up -d
```

## 🔧 Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
# API Configuration
API_TOKEN=tu_token_de_32_caracteres

# AI Model API Keys
OPENAI_API_KEY=tu_clave_openai
ANTHROPIC_API_KEY=tu_clave_anthropic
GOOGLE_API_KEY=tu_clave_google
MISTRAL_API_KEY=tu_clave_mistral
COHERE_API_KEY=tu_clave_cohere

# 📊 BigQuery Configuration (Opcional - para métricas avanzadas)
BIGQUERY_PROJECT_ID=tu-proyecto-google-cloud
BIGQUERY_DATASET=security_metrics
BIGQUERY_LOCATION=us-central1
BIGQUERY_MAX_BYTES_BILLED=1000000000
GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type": "service_account", "project_id": "tu-proyecto", ...}'
```

## 📊 Configuración de BigQuery (Opcional)

### Beneficios de BigQuery
- **Métricas en tiempo real**: Tracking de requests, tiempos de respuesta, modelos utilizados
- **Análisis de patrones**: Detección de tendencias de seguridad y uso
- **Monitoreo de errores**: Seguimiento de fallos y performance
- **Reportes automáticos**: Dashboards y alertas basados en datos

### Configuración Paso a Paso

1. **Crear Proyecto en Google Cloud**
   ```bash
   # Crear proyecto (opcional)
   gcloud projects create tu-proyecto-seguridad
   ```

2. **Habilitar BigQuery API**
   ```bash
   gcloud services enable bigquery.googleapis.com
   ```

3. **Crear Service Account**
   ```bash
   gcloud iam service-accounts create seguridad-bigquery \
     --display-name="Security Agent BigQuery"
   ```

4. **Asignar Permisos**
   ```bash
   gcloud projects add-iam-policy-binding tu-proyecto \
     --member="serviceAccount:seguridad-bigquery@tu-proyecto.iam.gserviceaccount.com" \
     --role="roles/bigquery.admin"
   ```

5. **Generar Clave JSON**
   ```bash
   gcloud iam service-accounts keys create credentials.json \
     --iam-account=seguridad-bigquery@tu-proyecto.iam.gserviceaccount.com
   ```

6. **Configurar Variable de Entorno**
   - Copia el contenido de `credentials.json`
   - Pégalo en `GOOGLE_APPLICATION_CREDENTIALS_JSON` en tu `.env`
   - Asegúrate de escapar las comillas correctamente

### Verificar Configuración BigQuery
```bash
# Verificar logs del contenedor
docker logs seguridad | grep -i bigquery

# Deberías ver:
# ✅ BigQuery client configured successfully
# ✅ Dataset 'security_metrics' ready
# ✅ Table 'security_analysis_metrics' ready
```

## 🐳 Docker Compose para Producción

El archivo `docker-compose.yml` está configurado para:
- **Traefik** como reverse proxy
- **Portainer** para gestión
- **Red tiendasneto** para comunicación entre agentes
- **Health checks** automáticos
- **Resource limits** apropiados

## 🌐 Configuración de Dominio

El servicio estará disponible en:
- **URL**: https://seguridad.tiendasnetows.com
- **Puerto**: 1401
- **Documentación**: https://seguridad.tiendasnetows.com/docs

## 🔍 Verificación del Despliegue

```bash
# Verificar contenedores
docker ps

# Verificar logs
docker logs seguridad

# Verificar salud
curl http://localhost:1401/health
```

## 📦 Comandos Útiles

```bash
# Detener servicio
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicio
docker-compose restart

# Actualizar imagen
docker-compose pull && docker-compose up -d
```

## 🚨 Solución de Problemas

### Error: Docker Desktop no responde
- Verifica que Docker Desktop esté ejecutándose
- Reinicia Docker Desktop si es necesario

### Error: Puerto en uso
- Cambia el puerto en el docker-compose.yml
- O mata el proceso que usa el puerto 1401

### Error: Variables de entorno faltantes
- Asegúrate de que el archivo .env exista
- Verifica que todas las variables estén definidas

### Verificar Mejoras de Detección
Para probar las nuevas capacidades de detección de hashes:
```bash
# Probar con hash MD5
curl -X POST "http://localhost:1401/analyze" \
  -H "Authorization: Bearer tu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "d14f169fbcbb2819042b6da635e86a16",
    "model": "openai:gpt-4o",
    "token": "tu_token",
    "agent": "agente-produccion"
  }'
```

## 📞 Soporte

Para problemas con el despliegue, contacta al equipo de infraestructura o revisa la documentación de Traefik/Portainer.

---

**¡Tu agente de seguridad está listo para producción! 🎉**