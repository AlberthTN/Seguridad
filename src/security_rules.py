from typing import List, Dict
import re

PROMPT_INJECTION_KEYWORDS: List[str] = [
    # English
    "ignore previous instructions", "disregard", "override system", "jailbreak",
    "act as", "pretend to be", "developer mode", "system prompt", "disable safety",
    "no restrictions", "unfiltered", "bypass", "take over", "call tool", "run tool",
    # Spanish
    "ignora las instrucciones anteriores", "omitir instrucciones", "modo desarrollador",
    "sin restricciones", "desactiva la seguridad", "omitir validaciones", "prompt del sistema",
]

DATA_EXFILTRATION_KEYWORDS: List[str] = [
    # English
    "secret", "api key", "token", "password", "credential", "confidential", "classified",
    "private", "environment variable", "env var",
    # Spanish
    "secreto", "clave", "contraseña", "credencial", "confidencial", "clasificado",
    "privado", "variable de entorno",
]

CODE_EXECUTION_KEYWORDS: List[str] = [
    # English
    "run shell", "execute command", "powershell", "bash", "cmd", "download and run",
    "pip install", "npm install", "curl", "wget", "python -c",
    # Spanish
    "ejecuta comando", "descargar y ejecutar", "instala paquete", "comando",
]

DEPENDENCY_ATTACK_KEYWORDS: List[str] = [
    # English
    "install package from", "use my library", "pip install mypackage", "replace dependency",
    "substitute library", "from unknown repository", "use private registry", "change requirements",
    "upload to pypi", "dependency confusion",
    # Spanish
    "instala paquete desde", "usa mi librería", "reemplaza dependencia", "sustituye librería",
    "repositorio desconocido", "registro privado", "cambia requirements", "confusión de dependencias",
]

POLICY_OVERRIDE_KEYWORDS: List[str] = [
    # English
    "even if it's against policy", "ignore policy", "against the rules", "prohibited",
    # Spanish
    "aunque esté prohibido", "ignora la política", "va contra las reglas", "prohibido",
]

HARMFUL_ACTIONS_KEYWORDS: List[str] = [
    # English
    "malware", "phishing", "keylogger", "ddos", "exploit", "hack", "sql injection",
    # Spanish
    "malware", "phishing", "registrador de teclas", "ataque ddos", "explotar", "hackear",
    "inyección sql",
]

SUSPICIOUS_URL_PATTERN = re.compile(r"https?://[\w.-]+", re.IGNORECASE)

CATEGORY_WEIGHTS: Dict[str, float] = {
    "prompt_injection": 0.35,
    "data_exfiltration": 0.35,
    "code_execution": 0.25,
    "dependency_attack": 0.25,
    "policy_override": 0.25,
    "harmful_actions": 0.35,
    "suspicious_links": 0.20,
}

SUGGESTIONS_BY_CATEGORY: Dict[str, List[str]] = {
    "prompt_injection": [
        "No solicites ignorar instrucciones ni desactivar salvaguardas.",
        "Formula tu petición sin intentar cambiar el rol o las políticas del agente.",
    ],
    "data_exfiltration": [
        "Evita pedir secretos, credenciales o datos confidenciales.",
        "Usa datos simulados o anonimiza la información en tu solicitud.",
    ],
    "code_execution": [
        "Evita pedir ejecución de comandos o descargas no verificadas.",
        "Solicita pseudocódigo o explicación, no ejecución directa.",
    ],
    "dependency_attack": [
        "No modifiques dependencias ni uses repositorios no confiables.",
        "Solicita revisión de dependencias por fuentes oficiales y firmadas.",
    ],
    "policy_override": [
        "No pidas saltarte políticas o reglas.",
        "Reformula la petición de forma compatible con las políticas.",
    ],
    "harmful_actions": [
        "Evita solicitar ayuda para actividades ilícitas o dañinas.",
        "Limítate a fines educativos y éticos, sin instrucciones operativas.",
    ],
    "suspicious_links": [
        "Evita URLs sospechosas; usa fuentes verificadas y oficiales.",
    ],
}