from typing import List, Dict, Any
import uuid

def generate_http_method_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None
    
    methods_to_test = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    for ep in endpoints:
        for method in methods_to_test:
            if method.upper() != ep.method.upper():
                tests.append({
                    "scan_id": scan_id,
                    "project_id": project_id,
                    "endpoint_id": ep.id,
                    "attacker_account_id": account_id,
                    "victim_account_id": None,
                    "category": "HTTP_METHOD_DISCOVERY",
                    "name": f"Test {method} on {ep.path}",
                    "status": "generated",
                    "expected_secure_result": "405",
                    "request_template_json": {
                        "method": method,
                        "path": ep.path,
                        "query": {},
                        "body": {}
                    }
                })
    return tests
