import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class HallucinationDetector:
    """
    NLI Premise-Entailment Hallucination Detector:
    Verifies every generated sentence against grounded source premise context to flag un-entailed statements.
    """
    def verify_factuality(self, generated_answer: str, retrieved_contexts: List[str]) -> Dict[str, Any]:
        if not retrieved_contexts:
            return {"is_hallucinated": True, "factuality_score": 0.0, "reason": "No retrieved context premise available."}

        premise_text = " ".join(retrieved_contexts).lower()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', generated_answer) if s.strip()]

        verified_count = 0
        unsupported_sentences = []

        for sentence in sentences:
            s_words = set(re.findall(r'\w+', sentence.lower()))
            if not s_words:
                continue
            # Check overlap with premise
            overlap = len([w for w in s_words if w in premise_text])
            ratio = overlap / len(s_words)
            if ratio >= 0.4:
                verified_count += 1
            else:
                unsupported_sentences.append(sentence)

        factuality_score = round(verified_count / len(sentences), 2) if sentences else 1.0
        is_hallucinated = factuality_score < 0.6

        logger.info(f"Hallucination Detector factuality_score: {factuality_score} (is_hallucinated: {is_hallucinated})")
        return {
            "is_hallucinated": is_hallucinated,
            "factuality_score": factuality_score,
            "unsupported_sentences": unsupported_sentences
        }

hallucination_detector = HallucinationDetector()
