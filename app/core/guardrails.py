import re
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Injection attack signature patterns
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|above)\s+instructions',
    r'system\s+prompt\s+override',
    r'you\s+are\t+now\s+in\s+dan\s+mode',
    r'bypass\s+safety\s+filter'
]

# PII Regex Patterns
PII_PATTERNS = {
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
    "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
    "API_KEY": r'\b(?:sk-[a-zA-Z0-9]{32,}|pcsk_[a-zA-Z0-9]{32,})\b',
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
}

class GuardrailsShield:
    """
    Guardrails AI Shield: Scans input queries and output responses for PII redaction
    and blocks malicious prompt injection attempts.
    """
    def sanitize_input(self, text: str) -> Tuple[str, bool, str]:
        # Check prompt injection
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Blocked prompt injection attempt matching pattern: {pattern}")
                return "", True, "Blocked by Guardrails AI Shield: Prompt injection detected."

        # Redact PII
        sanitized = text
        for pii_type, pii_regex in PII_PATTERNS.items():
            sanitized = re.sub(pii_regex, f"[REDACTED_{pii_type}]", sanitized)

        return sanitized, False, ""

    def sanitize_output(self, text: str) -> str:
        sanitized = text
        for pii_type, pii_regex in PII_PATTERNS.items():
            sanitized = re.sub(pii_regex, f"[REDACTED_{pii_type}]", sanitized)
        return sanitized

guardrails_shield = GuardrailsShield()
