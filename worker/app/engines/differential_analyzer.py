from typing import Dict, Any, Tuple

def get_structural_keys(data: Any, prefix: str = "") -> set:
    keys = set()
    if isinstance(data, dict):
        for k, v in data.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            keys.add(new_prefix)
            keys.update(get_structural_keys(v, new_prefix))
    elif isinstance(data, list) and len(data) > 0:
        keys.update(get_structural_keys(data[0], f"{prefix}[]"))
    return keys

def compare_responses(baseline_resp: Dict[str, Any], mutated_resp: Dict[str, Any], baseline_status: int, mutated_status: int) -> float:
    """
    Returns a similarity score between 0.0 and 1.0.
    1.0 means structurally identical.
    """
    if baseline_status != mutated_status:
        return 0.0 # Status code change is a significant difference

    base_keys = get_structural_keys(baseline_resp)
    mutated_keys = get_structural_keys(mutated_resp)
    
    if not base_keys and not mutated_keys:
        return 1.0
        
    intersection = base_keys.intersection(mutated_keys)
    union = base_keys.union(mutated_keys)
    
    return len(intersection) / len(union) if union else 1.0
