import httpx
import time
import re
from typing import Dict, Any, Tuple
from urllib.parse import urlparse
import logging

from app.security.redaction import redact_payload

logger = logging.getLogger("flowshield_worker")

def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
    """Check if the target host is allowed by the Target Config."""
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return False
        
    for allowed in allowed_hosts:
        if allowed == "*" or host == allowed or host.endswith(f".{allowed}"):
            return True
    return False


def is_safe_path(url: str, allowed_paths: list[str], forbidden_paths: list[str]) -> bool:
    """Check if the path is allowed and not forbidden."""
    parsed = urlparse(url)
    path = parsed.path
    
    # 1. Check forbidden paths (blocklist takes precedence)
    for forbidden in forbidden_paths:
        if forbidden in path:
            return False
            
    # 2. Check allowed paths
    if not allowed_paths or "*" in allowed_paths or "/*" in allowed_paths:
        return True
        
    for allowed in allowed_paths:
        if allowed.endswith("/*"):
            prefix = allowed[:-2]
            if path.startswith(prefix):
                return True
        elif path == allowed:
            return True
            
    return False


def execute_http_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    json_body: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
    target_config: Any = None,
    dry_run: bool = False
) -> Tuple[int, Dict[str, Any], int, str]:
    """
    Executes an HTTP request and returns redacted details.
    Returns: (status_code, response_json_redacted, duration_ms, error_message)
    """
    allowed_hosts = target_config.allowed_hosts if target_config else None
    
    # QA Demo Fix: Rewrite localhost to vulnerable-saas for docker-internal communication
    if "localhost:9000" in url or "127.0.0.1:9000" in url:
        url = url.replace("localhost:9000", "vulnerable-saas:9000").replace("127.0.0.1:9000", "vulnerable-saas:9000")
        
    # Also rewrite allowed_hosts to match
    if allowed_hosts:
        allowed_hosts = [h.replace("localhost", "vulnerable-saas").replace("127.0.0.1", "vulnerable-saas") for h in allowed_hosts]

    # --- Safety Checks ---
    if allowed_hosts and not is_safe_url(url, allowed_hosts):
        return (0, {}, 0, f"Blocked: Host not in allowed list for url: {url}")
        
    if target_config:
        allowed_paths = target_config.allowed_paths
        forbidden_paths = target_config.forbidden_paths
        if not is_safe_path(url, allowed_paths, forbidden_paths):
            return (0, {}, 0, f"Blocked: Path is forbidden or not in allowed list for url: {url}")
            
    # Security block for DELETE (we enforce safety profile explicitly)
    if method.upper() == "DELETE" and target_config and not target_config.allow_delete_requests:
        return (0, {}, 0, "Blocked by safety profile: DELETE requests are not executed unless explicitly opted-in.")

    if dry_run:
        logger.info(f"[DRY_RUN] Would execute {method} {url}")
        return (0, {"message": "DRY RUN MODE"}, 0, None)
        
    start_time = time.time()
    error_msg = None
    resp_data = {}
    status_code = 0
    
    try:
        kwargs = {
            "method": method.upper(),
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": 10.0,
            "follow_redirects": True
        }
        
        if isinstance(json_body, str):
            kwargs["content"] = json_body.encode('utf-8')
        else:
            kwargs["json"] = json_body

        response = httpx.request(**kwargs)
        status_code = response.status_code
        try:
            resp_data = response.json()
        except:
            resp_data = {"text_content": response.text[:500]}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"HTTP request failed: {url} - {error_msg}")
        
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Redact response
    resp_redacted = redact_payload(resp_data)
    
    return status_code, resp_redacted, duration_ms, error_msg
