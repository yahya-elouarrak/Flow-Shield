from typing import List, Dict, Any
import uuid
import re

import os

def load_wordlist(wordlist_name: str | None, default_words: List[str]) -> List[str]:
    if not wordlist_name:
        return default_words
    filepath = os.path.join("/app/wordlists", wordlist_name)
    if not os.path.exists(filepath):
        return default_words
    try:
        with open(filepath, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return default_words

def generate_hidden_parameter_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID, target_config: Any = None) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    wordlist_name = target_config.selected_wordlist if target_config else None
    words = load_wordlist(wordlist_name, ["admin", "is_admin", "debug", "role", "test", "id"])
    
    query_params = {}
    for w in words[:20]: # Bound to top 20 to avoid huge query strings
        query_params[w] = "1"

    for ep in endpoints:
        if ep.method.upper() in ["GET", "DELETE"]:
            test_path = re.sub(r'\{[^}]+\}', "1", ep.path)
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "HIDDEN_PARAMETER",
                "name": f"Hidden Query Parameters on {ep.path}",
                "status": "generated",
                "expected_secure_result": "No structural change in response",
                "request_template_json": {
                    "method": ep.method,
                    "path": test_path,
                    "query": query_params,
                    "body": {}
                }
            })
    return tests
