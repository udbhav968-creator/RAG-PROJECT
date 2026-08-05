import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Pre-configured tenant credentials
TENANT_CREDENTIALS: Dict[str, Dict[str, Any]] = {
    "key_admin_001": {"tenant_id": "TENANT_GLOBAL", "role": "admin", "clearance": ["admin", "engineering", "finance", "public"]},
    "key_eng_002": {"tenant_id": "TENANT_ENG", "role": "engineering", "clearance": ["engineering", "public"]},
    "key_fin_003": {"tenant_id": "TENANT_FIN", "role": "finance", "clearance": ["finance", "public"]},
    "key_public_004": {"tenant_id": "TENANT_PUBLIC", "role": "public", "clearance": ["public"]}
}

class TenantRBACManager:
    """
    Multi-Tenant RBAC Manager: Validates tenant API keys and enforces
    Row-Level Security (RLS) filters across vector retrieval and graph searches.
    """
    def authenticate_key(self, api_key: Optional[str]) -> Dict[str, Any]:
        if not api_key or api_key not in TENANT_CREDENTIALS:
            # Default fallback for unauthenticated public requests
            return TENANT_CREDENTIALS["key_public_004"]
        return TENANT_CREDENTIALS[api_key]

    def build_rls_filter(self, tenant_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_info["tenant_id"],
            "allowed_clearance": tenant_info["clearance"]
        }

rbac_manager = TenantRBACManager()
