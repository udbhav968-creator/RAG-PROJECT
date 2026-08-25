import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SyntheticQAGenerator:
    """
    Synthetic QA Dataset Generator:
    Self-generates evaluation question-answer pairs from raw document corpora.
    """
    def generate_qa_pairs(self, document_text: str, count: int = 3) -> List[Dict[str, str]]:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', document_text) if len(s.strip()) > 15]
        qa_pairs = []

        for i, sentence in enumerate(sentences[:count], 1):
            words = sentence.split()
            subject = words[0] if words else "Document"
            qa_pairs.append({
                "id": f"synth_qa_{i}",
                "question": f"What details are provided regarding {subject}?",
                "ground_truth": sentence
            })

        logger.info(f"Synthetic QA Generator generated {len(qa_pairs)} evaluation QA pairs.")
        return qa_pairs

synthetic_qa_generator = SyntheticQAGenerator()
