from typing import List, Dict, Any
import uuid

def generate_api_doc_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID) -> List[Dict[str, Any]]:
    tests = []
    # Use unauthenticated or lowest privilege
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    # Base paths to check
    doc_paths = ["/openapi.json", "/swagger.json", "/docs", "/api/docs", "/swagger-ui.html", "/swagger"]
    
    # We only need to check these once per project, not per endpoint.
    for path in doc_paths:
        tests.append({
            "scan_id": scan_id,
            "project_id": project_id,
            "endpoint_id": endpoints[0].id if endpoints else None, 
            "attacker_account_id": account_id,
            "victim_account_id": None,
            "category": "API_DOC_DISCOVERY",
            "name": f"Check for exposed documentation at {path}",
            "status": "generated",
            "expected_secure_result": "404 or 403",
            "request_template_json": {
                "method": "GET",
                "path": path,
                "query": {},
                "body": {}
            }
        })
    return tests
