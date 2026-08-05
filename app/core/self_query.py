import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SelfQueryParser:
    """
    Self-Querying Engine: Parses natural language user queries to extract metadata
    filtering predicates (date, department, doc_type, threshold).
    """
    def parse_query_filters(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        filters = {}

        # Extract Year / Date
        year_match = re.search(r'\b(202[0-9])\b', query)
        if year_match:
            filters["year"] = int(year_match.group(1))

        # Extract Department
        if "engineering" in q_lower or "eng" in q_lower:
            filters["department"] = "engineering"
        elif "finance" in q_lower or "fin" in q_lower:
            filters["department"] = "finance"
        elif "legal" in q_lower:
            filters["department"] = "legal"

        # Extract Document Type
        if "manual" in q_lower or "guide" in q_lower:
            filters["doc_type"] = "manual"
        elif "spec" in q_lower or "specification" in q_lower:
            filters["doc_type"] = "specification"
        elif "audit" in q_lower or "report" in q_lower:
            filters["doc_type"] = "audit_report"

        return filters

self_query_engine = SelfQueryParser()
