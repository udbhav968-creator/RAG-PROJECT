import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class DynamicContextPruner:
    """
    Dynamic Context Pruning Engine (LLMLingua):
    Compresses long context prompts by filtering low-information filler words
    while preserving high-information entity keywords.
    """
    def prune_context(self, context_text: str, target_ratio: float = 0.5) -> str:
        words = context_text.split()
        if len(words) <= 10:
            return context_text

        # Keep capitalized words, numbers, and key terms
        pruned_words = [
            w for w in words 
            if w[0].isupper() or any(c.isdigit() for c in w) or len(w) > 4
        ]

        if not pruned_words:
            pruned_words = words[:int(len(words) * target_ratio)]

        result = " ".join(pruned_words)
        logger.info(f"Context Pruner compressed text from {len(words)} words to {len(pruned_words)} words ({round(100 * len(pruned_words)/len(words))}% remaining).")
        return result

context_pruner = DynamicContextPruner()
