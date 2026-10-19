from typing import List, Dict, Any
import uuid
import re

def generate_sspp_query_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    payloads = {
        "sspp_ampersand": "dummy%26admin=true",
        "sspp_hash": "dummy%23",
    }

    for ep in endpoints:
        test_path = re.sub(r'\{[^}]+\}', "1", ep.path)
        for name, payload in payloads.items():
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "SSPP_QUERY",
                "name": f"SSPP Query Injection ({name}) on {ep.path}",
                "status": "generated",
                "expected_secure_result": "No structural change/errors",
                "request_template_json": {
                    "method": ep.method,
                    "path": test_path,
                    "query": {"test_param": payload},
                    "body": {}
                }
            })
    return tests
