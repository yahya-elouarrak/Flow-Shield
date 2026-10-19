from typing import List, Dict, Any
import uuid

def generate_business_logic_tests(
    endpoints: List[Any], 
    accounts: List[Any],
    scan_id: uuid.UUID,
    project_id: uuid.UUID
) -> List[Dict[str, Any]]:
    """
    Generate Business Logic workflow tests.
    Uses hardcoded deterministic resource IDs.
    Returns multi-step tests.
    """
    if len(accounts) == 0:
        return []
        
    attacker = accounts[0]
    test_cases = []

    # 1. Coupon Reuse (Apply coupon twice)
    test_cases.append({
        "scan_id": scan_id,
        "project_id": project_id,
        "endpoint_id": None,
        "attacker_account_id": attacker.id,
        "victim_account_id": None,
        "category": "BUSINESS_LOGIC",
        "name": "BUSINESS LOGIC: Coupon Reuse",
        "status": "generated",
        "expected_secure_result": "400 Bad Request on second apply",
        "request_template_json": {
            "is_multistep": True,
            "steps": [
                {
                    "method": "POST",
                    "path": "/coupons/apply",
                    "query": {},
                    "body": {"subscription_id": "sub-001", "code": "SAVE20"}
                },
                {
                    "method": "POST",
                    "path": "/coupons/apply",
                    "query": {},
                    "body": {"subscription_id": "sub-001", "code": "SAVE20"}
                }
            ]
        }
    })

    # 2. Payment Bypass (Activate subscription without payment)
    test_cases.append({
        "scan_id": scan_id,
        "project_id": project_id,
        "endpoint_id": None,
        "attacker_account_id": attacker.id,
        "victim_account_id": None,
        "category": "BUSINESS_LOGIC",
        "name": "BUSINESS LOGIC: Payment Bypass (Activation)",
        "status": "generated",
        "expected_secure_result": "400 Bad Request (payment not confirmed)",
        "request_template_json": {
            "is_multistep": True,
            "steps": [
                {
                    "method": "POST",
                    "path": "/subscriptions/select-plan",
                    "query": {},
                    "body": {"plan_id": "plan-basic"}
                },
                {
                    "method": "POST",
                    "path": "/subscriptions/activate",
                    "query": {},
                    "body": {"plan_id": "plan-basic"}
                }
            ]
        }
    })

    # 3. Price Manipulation / Negative Amount (Checkout)
    test_cases.append({
        "scan_id": scan_id,
        "project_id": project_id,
        "endpoint_id": None,
        "attacker_account_id": attacker.id,
        "victim_account_id": None,
        "category": "BUSINESS_LOGIC",
        "name": "BUSINESS LOGIC: Price Manipulation (Negative Amount)",
        "status": "generated",
        "expected_secure_result": "400 Bad Request",
        "request_template_json": {
            "is_multistep": True,
            "steps": [
                {
                    "method": "POST",
                    "path": "/payments/checkout",
                    "query": {},
                    "body": {"subscription_id": "sub-001", "amount": -100.0}
                }
            ]
        }
    })

    # 4. Duplicate Refund Request
    test_cases.append({
        "scan_id": scan_id,
        "project_id": project_id,
        "endpoint_id": None,
        "attacker_account_id": attacker.id,
        "victim_account_id": None,
        "category": "BUSINESS_LOGIC",
        "name": "BUSINESS LOGIC: Duplicate Refund Request",
        "status": "generated",
        "expected_secure_result": "400 Bad Request on second refund",
        "request_template_json": {
            "is_multistep": True,
            "steps": [
                {
                    "method": "POST",
                    "path": "/refunds/request",
                    "query": {},
                    "body": {"invoice_id": "inv-001", "amount": 1.0, "reason": "First refund"}
                },
                {
                    "method": "POST",
                    "path": "/refunds/request",
                    "query": {},
                    "body": {"invoice_id": "inv-001", "amount": 1.0, "reason": "Second refund"}
                }
            ]
        }
    })

    return test_cases
