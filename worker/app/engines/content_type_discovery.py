from typing import List, Dict, Any
import uuid

def generate_content_type_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    for ep in endpoints:
        if ep.method.upper() in ["POST", "PUT", "PATCH"]:
            
            # Form Encoded Test
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "CONTENT_TYPE_DISCOVERY",
                "name": f"Test application/x-www-form-urlencoded on {ep.path}",
                "status": "generated",
                "expected_secure_result": "415",
                "request_template_json": {
                    "method": ep.method,
                    "path": ep.path,
                    "query": {},
                    "body": "test_content_type=1",
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"}
                }
            })
            
            # XML Test
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "CONTENT_TYPE_DISCOVERY",
                "name": f"Test application/xml on {ep.path}",
                "status": "generated",
                "expected_secure_result": "415",
                "request_template_json": {
                    "method": ep.method,
                    "path": ep.path,
                    "query": {},
                    "body": "<root><test_content_type>1</test_content_type></root>",
                    "headers": {"Content-Type": "application/xml"}
                }
            })
    return tests
