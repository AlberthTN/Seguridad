from typing import Tuple
import re

from .security_rules import (
    PROMPT_INJECTION_KEYWORDS,
    DATA_EXFILTRATION_KEYWORDS,
    CODE_EXECUTION_KEYWORDS,
    DEPENDENCY_ATTACK_KEYWORDS,
    POLICY_OVERRIDE_KEYWORDS,
    HARMFUL_ACTIONS_KEYWORDS,
    SUSPICIOUS_URL_PATTERN,
    CATEGORY_WEIGHTS,
    SUGGESTIONS_BY_CATEGORY,
)
from .security_model import SecurityRequest, SecurityResult


def _has_hits(text: str, keywords) -> Tuple[bool, list]:
    """Devuelve (hay_coincidencias, lista_de_hits) basado en coincidencias (case-insensitive)."""
    text_lower = text.lower()
    hits = [kw for kw in keywords if kw in text_lower]
    return bool(hits), hits


def analyze_request(req: SecurityRequest) -> SecurityResult:
    """Analiza la solicitud y devuelve un SecurityResult con veredicto y razones.

    Política de scoring:
    - Si una categoría tiene algún hit, asigna el peso completo de la categoría.
    - Si no tiene hits, asigna 0.
    - Umbral: total_score < 0.25 => seguro; total_score >= 0.25 => no seguro.
    """
    text = req.input.strip()

    cat_scores = {}
    reasons = []
    suggestions = []

    # Prompt injection
    has, hits = _has_hits(text, PROMPT_INJECTION_KEYWORDS)
    w = CATEGORY_WEIGHTS["prompt_injection"]
    cat_scores["prompt_injection"] = w if has else 0.0
    if has:
        reasons.append(f"Intento de prompt injection: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["prompt_injection"]

    # Data exfiltration
    has, hits = _has_hits(text, DATA_EXFILTRATION_KEYWORDS)
    w = CATEGORY_WEIGHTS["data_exfiltration"]
    cat_scores["data_exfiltration"] = w if has else 0.0
    if has:
        reasons.append(f"Posible exfiltración de datos: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["data_exfiltration"]

    # Code execution
    has, hits = _has_hits(text, CODE_EXECUTION_KEYWORDS)
    w = CATEGORY_WEIGHTS["code_execution"]
    cat_scores["code_execution"] = w if has else 0.0
    if has:
        reasons.append(f"Solicitud de ejecución de código/comandos: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["code_execution"]

    # Dependency attack
    has, hits = _has_hits(text, DEPENDENCY_ATTACK_KEYWORDS)
    w = CATEGORY_WEIGHTS["dependency_attack"]
    cat_scores["dependency_attack"] = w if has else 0.0
    if has:
        reasons.append(f"Intento de ataque de dependencias: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["dependency_attack"]

    # Policy override
    has, hits = _has_hits(text, POLICY_OVERRIDE_KEYWORDS)
    w = CATEGORY_WEIGHTS["policy_override"]
    cat_scores["policy_override"] = w if has else 0.0
    if has:
        reasons.append(f"Intento de evadir políticas: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["policy_override"]

    # Harmful actions
    has, hits = _has_hits(text, HARMFUL_ACTIONS_KEYWORDS)
    w = CATEGORY_WEIGHTS["harmful_actions"]
    cat_scores["harmful_actions"] = w if has else 0.0
    if has:
        reasons.append(f"Acciones potencialmente dañinas: {', '.join(hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["harmful_actions"]

    # Suspicious links
    link_hits = SUSPICIOUS_URL_PATTERN.findall(text)
    w = CATEGORY_WEIGHTS["suspicious_links"]
    cat_scores["suspicious_links"] = w if link_hits else 0.0
    if link_hits:
        reasons.append(f"URLs sospechosas detectadas: {', '.join(link_hits)}")
        suggestions += SUGGESTIONS_BY_CATEGORY["suspicious_links"]

    # Score agregado
    total_score = sum(cat_scores.values())

    # Umbral de seguridad (ajustable):
    # Menor a 0.25 => seguro (True); mayor o igual a 0.25 => no seguro (False)
    is_safe = total_score < 0.25

    return SecurityResult(
        is_safe=is_safe,
        score=round(total_score, 3),
        category_scores={k: round(v, 3) for k, v in cat_scores.items()},
        reasons=reasons,
        suggestions=suggestions,
    )