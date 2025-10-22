from typing import List, Dict, Tuple
import re
import base64
import binascii
from langdetect import detect, DetectorFactory, LangDetectException

# Configurar semilla para resultados consistentes
DetectorFactory.seed = 0

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

# Patrones para detectar contenido encriptado/codificado
BASE64_PATTERN = re.compile(r"^[A-Za-z0-9+/]{20,}={0,2}$")
HEX_PATTERN = re.compile(r"^[0-9a-fA-F]{16,}$")
HASH_PATTERNS = [
    re.compile(r"^[a-fA-F0-9]{32}$"),  # MD5
    re.compile(r"^[a-fA-F0-9]{40}$"),  # SHA1
    re.compile(r"^[a-fA-F0-9]{64}$"),  # SHA256
    re.compile(r"^[a-fA-F0-9]{128}$"), # SHA512
    re.compile(r"^[a-fA-F0-9]{16}$"),  # MD2 (16 caracteres hex)
]

# Patrones para detectar caracteres sospechosos o texto sin sentido
NONSENSE_PATTERNS = [
    re.compile(r"[^\w\s\.,;:!?¿¡\-\(\)\"\'áéíóúñü]{3,}"),  # Secuencias de caracteres especiales
    re.compile(r"(.)\1{10,}"),  # Repetición excesiva del mismo carácter
    re.compile(r"^[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{10,}$"),  # Solo consonantes
    re.compile(r"[0-9]{20,}"),  # Secuencias muy largas de números
]

CATEGORY_WEIGHTS: Dict[str, float] = {
    "prompt_injection": 0.20,
    "data_exfiltration": 0.20,
    "code_execution": 0.15,
    "dependency_attack": 0.15,
    "policy_override": 0.15,
    "harmful_actions": 0.20,
    "suspicious_links": 0.10,
    "encrypted_content": 0.35,  # Aumentado para detectar mejor hashes y contenido encriptado
    "non_spanish_content": 0.30,  # Aumentado para bloquear mejor contenido no español
    "nonsense_content": 0.15,  # Nueva categoría para contenido sin sentido
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
    "encrypted_content": [
        "No envíes contenido encriptado, codificado en base64, hexadecimal o hasheado.",
        "Proporciona tu solicitud en texto plano y claro en español.",
    ],
    "non_spanish_content": [
        "Escribe tu solicitud únicamente en español.",
        "Evita usar otros idiomas o caracteres especiales no estándar.",
    ],
    "nonsense_content": [
        "Asegúrate de que tu mensaje tenga sentido y sea coherente.",
        "Evita enviar texto aleatorio, caracteres sin significado o secuencias extrañas.",
     ],
}


def is_base64_encoded(text: str) -> bool:
    """Detecta si el texto está codificado en base64."""
    try:
        # Eliminar espacios en blanco
        clean_text = text.replace(" ", "").replace("\n", "").replace("\t", "")
        
        # Verificar patrón base64
        if not BASE64_PATTERN.match(clean_text):
            return False
            
        # Intentar decodificar
        base64.b64decode(clean_text, validate=True)
        return len(clean_text) > 20  # Solo considerar secuencias largas
    except Exception:
        return False


def is_hex_encoded(text: str) -> bool:
    """Detecta si el texto está codificado en hexadecimal."""
    try:
        clean_text = text.replace(" ", "").replace("\n", "").replace("\t", "")
        if HEX_PATTERN.match(clean_text):
            bytes.fromhex(clean_text)
            return True
        return False
    except Exception:
        return False


def is_hash_like(text: str) -> bool:
    """Detecta si el texto parece un hash (MD5, SHA1, SHA256, SHA512)."""
    clean_text = text.replace(" ", "").replace("\n", "").replace("\t", "")
    return any(pattern.match(clean_text) for pattern in HASH_PATTERNS)


def detect_encrypted_content(text: str) -> Tuple[float, List[str]]:
    """
    Detecta contenido encriptado o codificado de manera optimizada.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Tuple con (score, reasons)
    """
    if not text or len(text.strip()) < 10:
        return 0.0, []
    
    reasons = []
    max_score = 0.0
    
    # Dividir en tokens para análisis más eficiente
    tokens = text.split()
    
    for token in tokens:
        token = token.strip()
        if len(token) < 10:  # Ignorar tokens muy cortos
            continue
            
        # Verificar Base64 (más eficiente con pre-filtro)
        if len(token) >= 20 and token.replace('=', '').replace('+', '').replace('/', '').isalnum():
            if is_base64_encoded(token):
                max_score = max(max_score, 0.9)
                reasons.append(f"Contenido Base64 detectado: {token[:20]}...")
                continue
        
        # Verificar Hex (solo si es alfanumérico y longitud apropiada)
        if len(token) >= 16 and token.isalnum() and all(c in '0123456789abcdefABCDEF' for c in token):
            if is_hex_encoded(token):
                max_score = max(max_score, 0.8)
                reasons.append(f"Contenido hexadecimal detectado: {token[:20]}...")
                continue
        
        # Verificar hashes (para longitudes específicas de hash conocidos)
        if len(token) in [16, 32, 40, 64, 128] and token.isalnum():
            if is_hash_like(token):
                max_score = max(max_score, 0.9)  # Aumentado el score para hashes
                reasons.append(f"Hash detectado (posible MD2/MD5/SHA): {token[:20]}...")
    
    return max_score, reasons


def detect_non_spanish_content(text: str) -> Tuple[float, List[str]]:
    """
    Detecta contenido que no está en español usando detección inteligente de idioma.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Tuple con (score, reasons)
    """
    if not text or len(text.strip()) < 10:
        return 0.0, []
    
    # Limpiar el texto para análisis
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    if len(clean_text) < 10:
        return 0.0, []
    
    try:
        # Usar langdetect para detectar el idioma
        detected_language = detect(clean_text)
        
        # Si no es español, calcular score basado en confianza
        if detected_language != 'es':
            # Score alto para idiomas claramente no españoles
            if detected_language in ['en', 'fr', 'de', 'it', 'pt']:
                return 0.8, [f"Contenido detectado en idioma '{detected_language}' en lugar de español"]
            else:
                return 0.6, [f"Contenido detectado en idioma '{detected_language}' en lugar de español"]
        
        return 0.0, []
        
    except LangDetectException:
        # Si no se puede detectar el idioma, verificar si hay caracteres no latinos
        non_latin_chars = len(re.findall(r'[^\x00-\x7F\u00C0-\u017F]', text))
        total_chars = len(text.replace(' ', ''))
        
        if total_chars > 0 and non_latin_chars / total_chars > 0.3:
            return 0.5, ["Contenido con caracteres no latinos detectado"]
        
        return 0.0, []


def detect_nonsense_content(text: str) -> Tuple[bool, List[str]]:
    """Detecta texto sin sentido o con patrones sospechosos."""
    issues = []
    
    for pattern in NONSENSE_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            issues.append(f"Patrón sospechoso detectado: {matches[0][:20]}...")
    
    # Verificar ratio de caracteres alfanuméricos vs especiales
    alphanumeric = sum(1 for c in text if c.isalnum() or c.isspace())
    total_chars = len(text)
    
    if total_chars > 10 and alphanumeric / total_chars < 0.7:
        issues.append("Demasiados caracteres especiales o no alfanuméricos")
    
    return bool(issues), issues