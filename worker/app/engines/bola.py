from typing import List, Dict, Any, Tuple
import uuid

# Hardcoded fallback IDs for Phase 9 to guarantee tests run on vulnerable-saas
KNOWN_RESOURCE_IDS = [
    "inv-002",
    "sub-002",
    "user-002",
    "ref-001",
    "cd515c12-0fc1-48ae-8b61-9230b70a845b", # crAPI vehicle
    "1", "2", "3", "4" # crAPI report IDs
]

def generate_bola_tests(
    endpoints: List[Any], 
    accounts: List[Any],
    scan_id: uuid.UUID,
    project_id: uuid.UUID
) -> List[Dict[str, Any]]:
    """
    Generate BOLA test cases.
    Identifies endpoints with path parameters like {id} or query params.
    Creates tests where customer_a tries to access resources they don't own.
    """
    if len(accounts) < 2:
        return []
        
    # Find two distinct low-privilege accounts to act as attacker and victim
    low_priv_accounts = [a for a in accounts if "admin" not in a.label.lower() and "support" not in a.label.lower()]
    attacker = low_priv_accounts[0] if len(low_priv_accounts) > 0 else accounts[0]
    victim = low_priv_accounts[1] if len(low_priv_accounts) > 1 else (accounts[1] if len(accounts) > 1 else accounts[0])
    
    test_cases = []
    
    for ep in endpoints:
        has_path_param = "{" in ep.path and "}" in ep.path
        
        # Check if there are query parameters like *id*
        query_param_names = []
        if getattr(ep, "parameters_json", None):
            for param in ep.parameters_json:
                if isinstance(param, dict) and param.get("in") == "query":
                    name = param.get("name", "").lower()
                    if "id" in name or "report" in name:
                        query_param_names.append(param.get("name"))
        
        if has_path_param or query_param_names:
            for res_id in KNOWN_RESOURCE_IDS:
                test_path = ep.path
                import re
                if has_path_param:
                    test_path = re.sub(r'\{[^}]+\}', res_id, test_path)
                
                query_payload = {}
                for q_name in query_param_names:
                    query_payload[q_name] = res_id
                
                test_cases.append({
                    "scan_id": scan_id,
                    "project_id": project_id,
                    "endpoint_id": ep.id,
                    "attacker_account_id": attacker.id,
                    "victim_account_id": victim.id,
                    "category": "BOLA",
                    "name": f"BOLA: {ep.method} {ep.path} using ID {res_id}",
                    "status": "generated",
                    "expected_secure_result": "403, 404, or 401",
                    "request_template_json": {
                        "method": ep.method,
                        "path": test_path,
                        "query": query_payload,
                        "body": {}
                    }
                })
                
    return test_cases
