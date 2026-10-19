from typing import List, Dict, Any
import uuid
import re

def generate_sspp_structured_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    for ep in endpoints:
        if ep.method.upper() in ["POST", "PUT", "PATCH"]:
            test_path = re.sub(r'\{[^}]+\}', "1", ep.path)
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "SSPP_STRUCTURED",
                "name": f"SSPP Structured JSON Injection on {ep.path}",
                "status": "generated",
                "expected_secure_result": "Parsing error or no state change",
                "request_template_json": {
                    "method": ep.method,
                    "path": test_path,
                    "query": {},
                    "body": {"test_field": '1","admin":true,"x":"y'}
                }
            })
    return tests
