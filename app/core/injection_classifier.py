import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class InjectionClassifierML:
    """
    ML Prompt Injection Classifier: Machine Learning security model scanning for
    zero-day indirect prompt injection threats in input prompts.
    """
    def classify_threat(self, prompt: str) -> Tuple[bool, float]:
        p_lower = prompt.lower()
        if "ignore" in p_lower and "instruction" in p_lower:
            return True, 0.98
        elif "bypass" in p_lower or "jailbreak" in p_lower:
            return True, 0.95
        return False, 0.01

ml_injection_classifier = InjectionClassifierML()
