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
docker build -t alberth121484/seguridad:01.00.001 .
```

### 3. Probar la Imagen Localmente
```bash
docker run -p 1401:1401 -e API_TOKEN="tu_token" alberth121484/seguridad:01.00.001
```

### 4. Iniciar Sesión en Docker Hub
```bash
docker login
# Ingresa tus credenciales de Docker Hub
```

### 5. Subir la Imagen a Docker Hub
```bash
docker push alberth121484/seguridad:01.00.001
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

## 📞 Soporte

Para problemas con el despliegue, contacta al equipo de infraestructura o revisa la documentación de Traefik/Portainer.

---

**¡Tu agente de seguridad está listo para producción! 🎉**