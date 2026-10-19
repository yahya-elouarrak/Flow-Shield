from typing import List, Dict, Any
import uuid

from app.engines.bola import generate_bola_tests
from app.engines.bfla import generate_bfla_tests
from app.engines.mass_assignment import generate_mass_assignment_tests
from app.models import TestCase

def generate_all_tests(
    endpoints: List[Any], 
    accounts: List[Any],
    scan_job: Any,
    target_config: Any = None
) -> List[TestCase]:
    """
    Orchestrates the individual engines to generate test cases.
    Returns a list of TestCase model objects (unsaved).
    """
    options = scan_job.options_json or {}
    
    # Defaults (if frontend doesn't send specific toggles, enable all for now)
    enable_bola = options.get("enable_bola", True)
    enable_bfla = options.get("enable_bfla", True)
    enable_ma = options.get("enable_mass_assignment", True)
    
    raw_tests: List[Dict[str, Any]] = []
    
    if enable_bola:
        raw_tests.extend(generate_bola_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
        
    if enable_bfla:
        raw_tests.extend(generate_bfla_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
        
    if enable_ma:
        raw_tests.extend(generate_mass_assignment_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
        
    # Phase 3: Advanced API Testing Discovery Engines
    from app.engines.api_documentation_discovery import generate_api_doc_tests
    from app.engines.undocumented_endpoint_discovery import generate_undocumented_endpoint_tests
    from app.engines.http_method_discovery import generate_http_method_tests
    from app.engines.content_type_discovery import generate_content_type_tests
    
    raw_tests.extend(generate_api_doc_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
    raw_tests.extend(generate_undocumented_endpoint_tests(endpoints, accounts, scan_job.id, scan_job.project_id, target_config))
    raw_tests.extend(generate_http_method_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
    raw_tests.extend(generate_content_type_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
    
    # Phase 4: Parameter Pollution & Hidden Parameters
    from app.engines.hidden_parameter_discovery import generate_hidden_parameter_tests
    from app.engines.sspp_query import generate_sspp_query_tests
    from app.engines.sspp_path import generate_sspp_path_tests
    from app.engines.sspp_structured import generate_sspp_structured_tests
    
    raw_tests.extend(generate_hidden_parameter_tests(endpoints, accounts, scan_job.id, scan_job.project_id, target_config))
    raw_tests.extend(generate_sspp_query_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
    raw_tests.extend(generate_sspp_path_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
    raw_tests.extend(generate_sspp_structured_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
        
    # Always run business logic for this phase
    from app.engines.workflow import generate_business_logic_tests
    raw_tests.extend(generate_business_logic_tests(endpoints, accounts, scan_job.id, scan_job.project_id))
        
    test_cases = []
    for rt in raw_tests:
        tc = TestCase(
            scan_id=rt["scan_id"],
            project_id=rt["project_id"],
            endpoint_id=rt["endpoint_id"],
            attacker_account_id=rt["attacker_account_id"],
            victim_account_id=rt["victim_account_id"],
            category=rt["category"],
            name=rt["name"],
            status=rt["status"],
            expected_secure_result=rt["expected_secure_result"],
            request_template_json=rt["request_template_json"]
        )
        test_cases.append(tc)
        
    return test_cases
