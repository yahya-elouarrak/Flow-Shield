from typing import List, Dict, Any
import uuid

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

def generate_undocumented_endpoint_tests(endpoints: List[Any], accounts: List[Any], scan_id: uuid.UUID, project_id: uuid.UUID, target_config: Any = None) -> List[Dict[str, Any]]:
    tests = []
    account = accounts[0] if accounts else None
    account_id = account.id if account else None

    # Load words
    wordlist_name = target_config.selected_wordlist if target_config else None
    words = load_wordlist(wordlist_name, ["admin", "internal", "debug", "v1", "v2", "beta", "api", "test", "dev"])

    # We keep mutations bounded to avoid hitting rate limits.
    for ep in endpoints:
        path = ep.path
        mutations = []
        if "/v1/" in path:
            mutations.append(path.replace("/v1/", "/v2/"))
        elif "/v2/" in path:
            mutations.append(path.replace("/v2/", "/v1/"))
            
        if "{" not in path:
            # Strip trailing slash if present for cleaner appends
            base_path = path.rstrip("/")
            # Use top 10 words from wordlist to avoid exploding test cases if wordlist is huge
            for w in words[:10]:
                mutations.append(f"{base_path}/{w}")
            
        for mut in mutations:
            tests.append({
                "scan_id": scan_id,
                "project_id": project_id,
                "endpoint_id": ep.id,
                "attacker_account_id": account_id,
                "victim_account_id": None,
                "category": "UNDOCUMENTED_ENDPOINT",
                "name": f"Check for undocumented endpoint at {mut}",
                "status": "generated",
                "expected_secure_result": "404",
                "request_template_json": {
                    "method": ep.method,
                    "path": mut,
                    "query": {},
                    "body": {}
                }
            })
    return tests
