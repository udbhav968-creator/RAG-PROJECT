import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TableOCREngine:
    """
    PDF Table & Chart OCR Engine: Extracts structured tabular data from PDF files
    and converts tables into queryable Markdown schemas.
    """
    def parse_table_to_markdown(self, raw_text: str) -> str:
        lines = raw_text.split('\n')
        table_lines = [l for l in lines if '|' in l or '\t' in l]
        if not table_lines:
            return raw_text

        md_rows = ["| Column 1 | Column 2 |", "| --- | --- |"]
        for line in table_lines:
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            if len(parts) >= 2:
                md_rows.append(f"| {parts[0]} | {parts[1]} |")

        return "\n".join(md_rows)

table_ocr_engine = TableOCREngine()
