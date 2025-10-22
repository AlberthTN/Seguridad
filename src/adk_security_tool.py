from typing import Dict

from security_model import SecurityRequest
from security_analyzer import analyze_request


def analyze_security(user_input: str) -> Dict:
    """Analyze a user instruction for security risks and return a JSON-friendly dict.

    Args:
        user_input (str): The text to analyze for security threats (prompt injection,
            data exfiltration, code execution, dependency attacks, policy override,
            harmful actions, suspicious links).

    Returns:
        Dict: A dictionary with keys:
            - is_safe (bool): True if safe, False otherwise
            - score (float): aggregated risk score
            - category_scores (dict[str, float]): scores per category
            - reasons (list[str]): matched reasons
            - suggestions (list[str]): mitigation suggestions
    """
    req = SecurityRequest(input=user_input)
    result = analyze_request(req)
    return result.to_json()