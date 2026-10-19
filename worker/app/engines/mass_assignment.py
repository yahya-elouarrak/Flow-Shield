from typing import List, Dict, Any
import uuid

UNAUTHORIZED_FIELDS = {
    "role": "admin",
    "is_admin": True,
    "isAdmin": True,
    "subscription_status": "premium",
    "balance": 999999,
    "price": 1,
    "amount": -100
}

def generate_mass_assignment_tests(
    endpoints: List[Any], 
    accounts: List[Any],
    scan_id: uuid.UUID,
    project_id: uuid.UUID
) -> List[Dict[str, Any]]:
    if not accounts:
        return []
        
    low_priv_accounts = [a for a in accounts if "admin" not in a.label.lower() and "support" not in a.label.lower()]
    attacker = low_priv_accounts[0] if low_priv_accounts else accounts[0]
    test_cases = []
    
    for ep in endpoints:
        if ep.method.upper() in ["POST", "PUT", "PATCH"]:
            test_path = ep.path
            import re
            test_path = re.sub(r'\{[^}]+\}', "inv-001", test_path)
            
            test_cases.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": attacker.id,
                "victim_account_id": None,
                "category": "MASS_ASSIGNMENT",
                "name": f"Multi-step Mass Assignment: {ep.method} {ep.path}",
                "status": "generated",
                "expected_secure_result": "Fields ignored (GET shows unmodified state)",
                "request_template_json": {
                    "is_multistep": True,
                    "steps": [
                        {
                            "method": ep.method,
                            "path": test_path,
                            "query": {},
                            "body": UNAUTHORIZED_FIELDS
                        },
                        {
                            "method": "GET",
                            "path": test_path,
                            "query": {},
                            "body": {}
                        }
                    ]
                }
            })
            
    return test_cases
