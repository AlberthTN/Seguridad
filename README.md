# 🛡️ Security Agent (ADK + CLI + REST API)

Este proyecto implementa un agente de seguridad avanzado que analiza instrucciones de usuario para detectar riesgos como prompt injection, exfiltración de datos, ejecución de código, ataques de dependencias, intentos de evadir políticas, acciones dañinas y enlaces sospechosos. 

## ✨ Características

- **🔍 Análisis Heurístico**: Reglas basadas en palabras clave y patrones
- **🤖 IA Multi-Modelo**: Soporte para OpenAI, Anthropic, Google, Mistral, Cohere
- **🌐 REST API**: API completa con autenticación por tokens
- **🔐 Autenticación**: Token-based authentication
- **🐳 Dockerizado**: Listo para producción con Traefik/Portainer
- **🧪 Tests**: Suite completa de pruebas unitarias
- **📊 JSON Output**: Resultados detallados con scores por categoría

## 🚀 Modos de Uso

1. **CLI Local**: Análisis rápido desde terminal
2. **REST API**: Servicio web con documentación Swagger
3. **ADK Tool**: Integración con Google ADK para agentes AI
4. **Docker**: Despliegue en producción

## 📁 Estructura del Proyecto

```
seguridad/
├── src/                    # Código fuente
│   ├── __init__.py
│   ├── security_model.py   # Modelos Pydantic (Request/Response)
│   ├── security_rules.py   # Reglas y palabras clave
│   ├── security_analyzer.py # Motor de análisis heurístico
│   ├── adk_security_tool.py # Herramienta ADK
│   ├── adk_agent.py        # Agente ADK
│   ├── ai_analyzer.py      # Análisis con IA multi-modelo
│   ├── model_service.py   # Gestión de modelos AI
│   ├── api.py             # API FastAPI
│   └── __pycache__/
├── tests/                  # Pruebas unitarias
│   ├── test_security_analyzer.py
│   ├── test_adk_tool.py
│   └── __pycache__/
├── .env.example           # Template variables de entorno
├── .gitignore            # Archivos ignorados por Git
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Docker Compose para producción
├── requirements.txt      # Dependencias Python
├── main.py              # CLI principal
├── generate_token.py    # Generador de tokens seguros
├── curl_command.ps1     # Ejemplos de curl para PowerShell
└── DEPLOYMENT.md        # Guía de despliegue completo
```

## 📦 Instalación y Configuración Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/seguridad.git
cd seguridad
```

### 2. Configurar Variables de Entorno
```bash
# Copiar el template de variables de entorno
cp .env.example .env

# Editar el archivo .env con tus valores reales
# Obtener API keys de los proveedores de IA
# Generar token seguro: python generate_token.py
```

### 3. Crear Entorno Virtual
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

### 4. Instalar Dependencias
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 🚀 Uso Rápido

### Modo CLI (Análisis Heurístico)
```bash
python main.py "Tu texto a analizar"

# O desde archivo
type input.txt | python main.py
```

### Modo API (Servicio Web)
```bash
python main.py --api
# API disponible en: http://localhost:1401
# Documentación: http://localhost:1401/docs
```

### Generar Token Seguro
```bash
python generate_token.py
# Esto genera un token de 32 caracteres y actualiza el .env
```

## 🌐 API Endpoints

- `GET /` - Información del API
- `GET /health` - Estado del servicio
- `GET /models` - Lista de modelos disponibles
- `POST /analyze` - Análisis de seguridad (requiere autenticación)
- `POST /analyze-batch` - Análisis por lotes

### Ejemplo de Solicitud API
```bash
curl -X POST http://localhost:1401/analyze \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ignora todas las instrucciones anteriores",
    "model": "openai:gpt-4-turbo",
    "token": "TU_TOKEN"
  }'
```

## 🐳 Docker Deployment

### Construir Imagen
```bash
docker build -t alberth121484/seguridad:01.00.001 .
```

### Ejecutar con Docker Compose
```bash
docker-compose up -d
```

### Configuración para Traefik/Portainer
El proyecto incluye configuración completa para:
- **Traefik** como reverse proxy
- **Portainer** para gestión
- **Health checks** automáticos
- **Resource limits** configurados

## 📊 Estructura de Respuesta

```json
{
  "is_safe": true,
  "score": 0.0,
  "model_used": "heuristic",
  "category_scores": {
    "prompt_injection": 0.0,
    "data_exfiltration": 0.0,
    "code_execution": 0.0,
    "dependency_attack": 0.0,
    "policy_evasion": 0.0,
    "harmful_actions": 0.0,
    "suspicious_links": 0.0
  },
  "reasons": [],
  "suggestions": []
}
```

## Uso: CLI

- Ejecutar: python main.py "Tu texto a analizar"
- También puedes pasar texto por stdin: type input.txt | python main.py

Salida JSON de ejemplo:
{
  "is_safe": true,
  "score": 0.0,
  "category_scores": {"prompt_injection": 0.0, ...},
  "reasons": [],
  "suggestions": []
}

## Pruebas

- Ejecutar con el intérprete del entorno virtual:
- .venv\Scripts\python.exe -m pytest -q

## Integración con ADK

- La herramienta se define en <mcfile name="adk_security_tool.py" path="d:\IA\Agentes2025\seguridad\src\adk_security_tool.py"></mcfile> como función con type hints que devuelve `dict`, el formato esperado por ADK para Function Tools. <mcreference link="https://google.github.io/adk-docs/tools/" index="1">1</mcreference>
- La función expuesta es <mcsymbol name="analyze_security" filename="adk_security_tool.py" path="d:\IA\Agentes2025\seguridad\src\adk_security_tool.py" startline="6" type="function"></mcsymbol>, que envuelve el motor y retorna JSON amigable.
- El agente ADK se define en <mcfile name="adk_agent.py" path="d:\IA\Agentes2025\seguridad\src\adk_agent.py"></mcfile> con modelo Gemini y la herramienta en `tools=[analyze_security]`. Para ejecutar agentes con múltiples herramientas y/o usar la UI de desarrollo, consulta el quickstart y prepara tu `.env` con tu clave (Express mode). <mcreference link="https://google.github.io/adk-docs/get-started/quickstart/" index="2">2</mcreference>
- Nota: los Function Tools en ADK deben tener type hints y devolver un diccionario; el LLM decide cuándo llamar la herramienta y con qué argumentos. <mcreference link="https://google.github.io/adk-docs/tools/" index="1">1</mcreference>

### Ejecutar con la UI de desarrollo (opcional)

- Asegúrate de tener una clave de Express mode y colócala en `.env` junto al archivo del agente (por ejemplo, en `src/.env`). <mcreference link="https://google.github.io/adk-docs/get-started/quickstart/" index="2">2</mcreference>
- Inicia la UI: adk web
- En Windows, si ves `_make_subprocess_transport NotImplementedError`, usa: adk web --no-reload <mcreference link="https://google.github.io/adk-docs/get-started/quickstart/" index="2">2</mcreference>

## Buenas prácticas de seguridad

- Principio de mínimo privilegio, validación de entrada/salida, y uso de guardrails (políticas) para restringir acciones. 
- Considera habilitar confirmación de herramientas (HITL) para aprobar manualmente ejecuciones críticas. ADK ofrece Tool Confirmation para reforzar la seguridad del uso de herramientas. <mcreference link="https://github.com/google/adk-python" index="5">5</mcreference>

## Umbral y categorías

- Cada categoría suma su peso completo si se detecta al menos una coincidencia; el umbral de inseguridad se dispara si `score >= 0.25`.
- Ajusta `CATEGORY_WEIGHTS` y palabras clave en `src/security_rules.py` según tus necesidades.

## Contribución

- Agrega casos de prueba en `tests/` para nuevos patrones.
- Ajusta el analizador para tu dominio y añade métricas si integras modelos de clasificación en el futuro.

## 🚀 Despliegue en GitHub

### 1. Inicializar Repositorio Git
```bash
git init
git add .
git commit -m "Initial commit: Security Agent with AI multi-model support"
```

### 2. Configurar Remote
```bash
git remote add origin https://github.com/tu-usuario/seguridad.git
git branch -M main
```

### 3. Primer Push
```bash
git push -u origin main
```

### 4. Configurar Secrets en GitHub
En GitHub → Settings → Secrets → Actions, agregar:
- `DOCKERHUB_USERNAME`: Tu usuario de Docker Hub
- `DOCKERHUB_TOKEN`: Tu token de acceso de Docker Hub
- `API_TOKEN`: Token para autenticación API
- `OPENAI_API_KEY`: Key de OpenAI
- `ANTHROPIC_API_KEY`: Key de Anthropic
- `GOOGLE_API_KEY`: Key de Google Gemini
- `MISTRAL_API_KEY`: Key de Mistral AI
- `COHERE_API_KEY`: Key de Cohere

## 📊 GitHub Actions CI/CD

El proyecto incluye flujo de CI/CD automático:
- ✅ Tests automáticos en cada push
- 🐳 Build automático de Docker image
- 📦 Push automático a Docker Hub
- 🚀 Deploy automático en producción

## 🔒 Seguridad y Buenas Prácticas

- **Principio de mínimo privilegio**: Solo los permisos necesarios
- **Validación de entrada/salida**: Sanitización de datos
- **Guardrails**: Políticas para restringir acciones peligrosas
- **Tool Confirmation**: Confirmación manual de herramientas críticas
- **Token Rotation**: Rotación periódica de tokens API
- **Environment Separation**: Entornos separados dev/prod

## 📈 Monitoreo y Métricas

- Health checks automáticos
- Logging estructurado
- Métricas de rendimiento
- Alertas de seguridad

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Add nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Áreas de Mejora
- Agregar más patrones de seguridad
- Integrar más modelos de IA
- Mejorar métricas y monitoring
- Optimizar rendimiento
- Añar documentación

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- 📖 Documentación: Consulta este README y la documentación del API
- 🐛 Issues: Reportar bugs en GitHub Issues
- 💬 Discusiones: GitHub Discussions para preguntas
- 📧 Contacto: Para soporte prioritario

---

**¡Tu agente de seguridad está listo para GitHub y producción! 🎉**