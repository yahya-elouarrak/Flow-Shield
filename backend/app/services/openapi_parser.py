"""
OpenAPI 3.x parser service.

Parses an OpenAPI specification (JSON or YAML), resolves local $ref,
extracts endpoints, and computes a heuristic sensitive_score for each.
"""

import re
import json
import yaml
from typing import Any, Dict, List, Optional, Tuple


# ─── Sensitive scoring keywords ──────────────────────────────────────────────

_SENSITIVE_KEYWORDS = {
    # Identity and access
    "user", "users", "account", "profile", "auth", "login", "register",
    "password", "token", "session", "me", "self",
    # Financial
    "order", "orders", "invoice", "payment", "refund", "charge",
    "subscription", "plan", "premium", "billing",
    "coupon", "discount", "wallet", "balance", "price", "amount",
    # Administrative
    "admin", "support", "role", "permission", "privilege",
    # Sensitive fields
    "status", "isadmin", "ispaid", "is_admin", "is_paid",
    "credit", "ssn", "email", "phone", "address",
}

_ID_PARAM_PATTERN = re.compile(r"\{(\w*id\w*)\}", re.IGNORECASE)


def _compute_sensitive_score(
    path: str,
    method: str,
    tags: List[str],
    path_params: List[str],
    query_params: List[str],
    body_fields: List[str],
) -> Tuple[int, List[str]]:
    """
    Calculate a 0-100 sensitive score and return the reasons.
    Higher score = more likely to be a security-sensitive endpoint.
    """
    score = 0
    reasons: List[str] = []

    # --- Path segment analysis ---
    path_lower = path.lower()
    path_segments = [seg for seg in path_lower.split("/") if seg and not seg.startswith("{")]
    for seg in path_segments:
        for kw in _SENSITIVE_KEYWORDS:
            if kw in seg:
                score += 15
                reasons.append(f"path contains '{kw}'")
                break  # one match per segment

    # --- ID path parameters (e.g. {userId}, {orderId}) ---
    id_matches = _ID_PARAM_PATTERN.findall(path)
    if id_matches:
        score += 10
        reasons.append(f"path has ID param(s): {', '.join(id_matches)}")

    # --- Method weighting ---
    m = method.upper()
    if m == "DELETE":
        score += 10
        reasons.append("DELETE method")
    elif m in ("PUT", "PATCH"):
        score += 5
        reasons.append(f"{m} method (state-changing)")
    elif m == "POST":
        score += 3

    # --- Tags ---
    for tag in tags:
        tag_lower = tag.lower()
        for kw in _SENSITIVE_KEYWORDS:
            if kw in tag_lower:
                score += 10
                reasons.append(f"tag '{tag}' contains '{kw}'")
                break

    # --- Parameter / body field names ---
    all_fields = [p.lower() for p in (path_params + query_params + body_fields)]
    for field in all_fields:
        for kw in _SENSITIVE_KEYWORDS:
            if kw in field:
                score += 5
                reasons.append(f"field '{field}' matches '{kw}'")
                break

    # Clamp to 0-100
    score = min(score, 100)
    # Deduplicate reasons while preserving order
    seen = set()
    unique_reasons = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    return score, unique_reasons


# ─── $ref resolver ───────────────────────────────────────────────────────────

def _resolve_ref(spec: Dict, ref: str) -> Optional[Dict]:
    """Resolve a local JSON $ref like '#/components/schemas/User'."""
    if not ref.startswith("#/"):
        return None
    parts = ref.lstrip("#/").split("/")
    current = spec
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current if isinstance(current, dict) else None


def _deep_resolve(spec: Dict, obj: Any, depth: int = 5) -> Any:
    """Recursively resolve $ref in a schema object up to a certain depth."""
    if depth <= 0 or obj is None:
        return obj
    if isinstance(obj, dict):
        if "$ref" in obj:
            resolved = _resolve_ref(spec, obj["$ref"])
            return _deep_resolve(spec, resolved, depth - 1) if resolved else obj
        return {k: _deep_resolve(spec, v, depth - 1) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_resolve(spec, item, depth - 1) for item in obj]
    return obj


# ─── Extract body fields ────────────────────────────────────────────────────

def _extract_body_fields(spec: Dict, request_body: Optional[Dict]) -> List[str]:
    """Extract top-level field names from a request body schema."""
    if not request_body:
        return []
    content = request_body.get("content", {})
    for media_type in ("application/json", "application/x-www-form-urlencoded"):
        media = content.get(media_type, {})
        schema = media.get("schema", {})
        schema = _deep_resolve(spec, schema, depth=3)
        if isinstance(schema, dict):
            props = schema.get("properties", {})
            if props:
                return list(props.keys())
    return []


# ─── Main parse function ────────────────────────────────────────────────────

def parse_openapi_spec(raw: str) -> Tuple[Dict, List[Dict]]:
    """
    Parse an OpenAPI spec (JSON or YAML string) and return:
      (spec_dict, list_of_endpoint_dicts)

    Raises ValueError on parse failure.
    """
    # Try JSON first, then YAML
    spec: Dict
    try:
        spec = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        try:
            spec = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            raise ValueError(f"Could not parse spec as JSON or YAML: {e}")

    if not isinstance(spec, dict):
        raise ValueError("Parsed spec is not a valid object/dictionary.")

    # Verify it looks like an OpenAPI spec
    if "openapi" not in spec and "swagger" not in spec:
        raise ValueError("Document does not appear to be an OpenAPI or Swagger specification.")

    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("No valid 'paths' object found in the specification.")

    # Global security schemes (for auth_required detection)
    global_security = spec.get("security", [])
    has_global_security = bool(global_security)

    endpoints: List[Dict] = []

    for path_str, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            operation = path_item.get(method)
            if not operation or not isinstance(operation, dict):
                continue

            # Extract basic metadata
            operation_id = operation.get("operationId")
            summary = operation.get("summary")
            description = operation.get("description")
            tags = operation.get("tags", [])
            if not isinstance(tags, list):
                tags = []

            # Auth required
            op_security = operation.get("security")
            if op_security is not None:
                # Explicit security on operation: empty list means no auth
                auth_required = bool(op_security)
            else:
                auth_required = has_global_security

            # Parameters
            raw_params = operation.get("parameters", []) + path_item.get("parameters", [])
            parameters_json = _deep_resolve(spec, raw_params, depth=3)

            path_params = []
            query_params = []
            for p in (parameters_json or []):
                if not isinstance(p, dict):
                    continue
                name = p.get("name", "")
                location = p.get("in", "")
                if location == "path":
                    path_params.append(name)
                elif location == "query":
                    query_params.append(name)

            # Also extract path params from the path template itself
            template_params = re.findall(r"\{(\w+)\}", path_str)
            for tp in template_params:
                if tp not in path_params:
                    path_params.append(tp)

            # Request body
            request_body = _deep_resolve(spec, operation.get("requestBody"), depth=3)
            request_schema = None
            if request_body:
                content = request_body.get("content", {})
                for mt in ("application/json", "application/x-www-form-urlencoded"):
                    if mt in content:
                        request_schema = _deep_resolve(spec, content[mt].get("schema"), depth=3)
                        break

            body_fields = _extract_body_fields(spec, request_body)

            # Response schema (just grab the first success response)
            response_schema = None
            responses = operation.get("responses", {})
            for code in ("200", "201", "default"):
                resp = responses.get(code)
                if resp and isinstance(resp, dict):
                    resp = _deep_resolve(spec, resp, depth=3)
                    resp_content = resp.get("content", {})
                    for mt in ("application/json",):
                        if mt in resp_content:
                            response_schema = _deep_resolve(
                                spec, resp_content[mt].get("schema"), depth=3
                            )
                            break
                    if response_schema:
                        break

            # Sensitive scoring
            method_upper = method.upper()
            sensitive_score, sensitive_reasons = _compute_sensitive_score(
                path_str, method_upper, tags, path_params, query_params, body_fields
            )

            endpoints.append({
                "method": method_upper,
                "path": path_str,
                "operation_id": operation_id,
                "summary": summary,
                "description": description,
                "tags": tags,
                "auth_required": auth_required,
                "parameters_json": parameters_json,
                "request_schema_json": request_schema,
                "response_schema_json": response_schema,
                "path_params": path_params,
                "query_params": query_params,
                "body_fields": body_fields,
                "sensitive_score": sensitive_score,
                "sensitive_reasons": sensitive_reasons,
            })

    return spec, endpoints
