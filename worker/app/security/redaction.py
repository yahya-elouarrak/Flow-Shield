import re
from typing import Any

SENSITIVE_KEYS = {
    "password", "secret", "token", "authorization",
    "access_token", "refresh_token", "api_key",
    "session", "cookie", "jwt", "bearer"
}

def redact_dict(data: dict) -> dict:
    """Recursively redact sensitive fields from dictionaries."""
    if not isinstance(data, dict):
        return data
    
    redacted = {}
    for key, value in data.items():
        k_lower = str(key).lower()
        if any(sensitive in k_lower for sensitive in SENSITIVE_KEYS):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = redact_dict(value)
        elif isinstance(value, list):
            redacted[key] = [redact_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            # Check for bearer token strings in values
            if isinstance(value, str) and value.lower().startswith("bearer "):
                redacted[key] = "Bearer [REDACTED]"
            else:
                redacted[key] = value
    return redacted

def redact_payload(payload: Any) -> Any:
    """Entry point for redaction."""
    if isinstance(payload, dict):
        return redact_dict(payload)
    if isinstance(payload, list):
        return [redact_dict(item) if isinstance(item, dict) else item for item in payload]
    return payload
