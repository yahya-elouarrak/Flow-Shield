from typing import List, Dict, Any
import uuid

PRIVILEGED_KEYWORDS = ["admin", "support", "refund", "role", "management", "mechanic", "merchant"]

def generate_bfla_tests(
    endpoints: List[Any], 
    accounts: List[Any],
    scan_id: uuid.UUID,
    project_id: uuid.UUID
) -> List[Dict[str, Any]]:
    """
    Generate BFLA test cases.
    Identifies privileged endpoints.
    Creates tests where a low privilege account attempts to access them.
    """
    if not accounts:
        return []
        
    # Find a low privilege account by checking label
    low_priv_accounts = [a for a in accounts if "admin" not in a.label.lower() and "support" not in a.label.lower()]
    attacker = low_priv_accounts[0] if low_priv_accounts else accounts[0]
    test_cases = []
    
    for ep in endpoints:
        path_lower = ep.path.lower()
        
        is_privileged = False
        if any(kw in path_lower for kw in PRIVILEGED_KEYWORDS):
            is_privileged = True
        if ep.method.upper() == "DELETE":
            is_privileged = True
            
        if is_privileged:
            # We replace path params with dummy UUIDs to ensure a valid URL structure
            test_path = ep.path
            import re
            test_path = re.sub(r'\{[^}]+\}', "user-001", test_path)
            
            test_cases.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": attacker.id,
                "victim_account_id": None,
                "category": "BFLA",
                "name": f"BFLA: {ep.method} {ep.path}",
                "status": "generated",
                "expected_secure_result": "401 or 403",
                "request_template_json": {
                    "method": ep.method,
                    "path": test_path,
                    "query": {},
                    "body": {}
                }
            })
            
    return test_cases
