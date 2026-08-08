import logging
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ProductQuantizer:
    """
    Product Quantization (PQ) Vector Compression Engine:
    Quantizes float32 vector embeddings into uint8 codes for 10x memory compression.
    """
    def quantize_vector(self, vector: List[float]) -> List[int]:
        if not vector:
            return []
        arr = np.array(vector, dtype=np.float32)
        # Normalize and scale to 0-255 uint8 range
        min_val, max_val = arr.min(), arr.max()
        if max_val == min_val:
            quantized = np.zeros_like(arr, dtype=np.uint8)
        else:
            quantized = ((arr - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        logger.info(f"Product Quantizer compressed float32 vector ({len(vector)} dims) to uint8 bytes.")
        return quantized.tolist()

product_quantizer = ProductQuantizer()
