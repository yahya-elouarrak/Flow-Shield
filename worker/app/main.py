import os
import time
import logging
import httpx
import base64
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlmodel import Session, select
from sqlalchemy.orm import with_expression

from app.models import ScanJob, ScanEvent, Project, TargetConfig, Endpoint, Account

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("flowshield_worker")


def get_engine():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL is missing!")
        return None
    return create_engine(db_url)


def write_event(session: Session, scan_id, phase, message, level="info"):
    event = ScanEvent(
        scan_id=scan_id,
        phase=phase,
        message=message,
        level=level
    )
    session.add(event)
    logger.info(f"Scan {scan_id} [{phase}] {level.upper()}: {message}")


def process_scan(session: Session, job: ScanJob):
    logger.info(f"Processing scan job {job.id} for project {job.project_id}")
    scan_id = job.id
    
    try:
        # Phase 1: Loading Project
        job.phase = "loading"
        job.progress = 10
        write_event(session, scan_id, "loading", "Loading project data...")
        session.commit()
        time.sleep(1) # simulate work
        
        project = session.get(Project, job.project_id)
        if not project:
            raise ValueError("Project not found")

        # Phase 2: Loading Endpoints
        job.progress = 20
        write_event(session, scan_id, "loading", "Loading endpoint inventory...")
        session.commit()
        time.sleep(1)
        
        stmt = select(Endpoint).where(Endpoint.project_id == job.project_id)
        endpoints = session.exec(stmt).all()
        if not endpoints:
            raise ValueError("No endpoints found for project. Please import an API specification.")
        write_event(session, scan_id, "loading", f"Loaded {len(endpoints)} endpoints.")

        # Phase 3: Loading Accounts
        job.progress = 30
        write_event(session, scan_id, "loading", "Loading test accounts...")
        session.commit()
        time.sleep(1)
        
        stmt = select(Account).where(Account.project_id == job.project_id)
        accounts = session.exec(stmt).all()
        write_event(session, scan_id, "loading", f"Loaded {len(accounts)} test accounts.")

        # Phase 4: Validating Scope
        job.phase = "validating"
        job.progress = 40
        write_event(session, scan_id, "validating", "Validating scope and safety rules...")
        session.commit()
        time.sleep(1)
        
        stmt = select(TargetConfig).where(TargetConfig.project_id == job.project_id)
        target_config = session.exec(stmt).first()
        if not target_config:
            raise ValueError("Safety configuration (Target Config) not found for project.")
        
        write_event(session, scan_id, "validating", f"Allowed hosts: {', '.join(target_config.allowed_hosts)}")

        # Phase 5: Planning
        job.phase = "planning"
        job.progress = 60
        write_event(session, scan_id, "planning", "Generating security test cases...")
        session.commit()
        
        from app.engines.test_generator import generate_all_tests
        test_cases = generate_all_tests(endpoints, accounts, job, target_config)
        
        # --- AI Planner Integration ---
        if job.ai_enabled:
            write_event(session, scan_id, "planning", "AI Planner enabled. Invoking AI Planner (Groq) for endpoint classification and test generation...")
            from app.engines.ai_planner import classify_endpoint, suggest_test_cases
            from app.models import TestCase
            import uuid
            
            ai_generated_tests = []
            roles = [acc.label for acc in accounts]
            
            for ep in endpoints:
                try:
                    # Sanitize prompt payload
                    params = ep.parameters_json or []
                    body_schema = ep.request_schema_json or {}
                    
                    # Call AI to classify
                    classification = classify_endpoint(ep.method, ep.path, ep.tags, params, body_schema)
                    if classification:
                        # Call AI to suggest tests
                        suggestions = suggest_test_cases(ep.method, ep.path, classification, roles)
                        for sug in suggestions:
                            # Try to match the attacker role back to an account ID
                            attacker_acc = next((a for a in accounts if a.label == sug.attacker_role), accounts[0] if accounts else None)
                            if not attacker_acc:
                                continue
                                
                            # Convert to a real TestCase (Deterministic engines will handle actual execution via templates)
                            # To keep it simple, we use a basic GET/POST template based on the suggestion
                            req_template = {
                                "method": sug.endpoint_method or ep.method,
                                "path": sug.endpoint_path or ep.path,
                                "query": {},
                                "body": {}
                            }
                            
                            ai_tc = TestCase(
                                id=uuid.uuid4(),
                                scan_id=scan_id,
                                project_id=job.project_id,
                                endpoint_id=ep.id,
                                category=f"AI_{sug.category.upper()}",
                                name=f"[AI] {sug.name}",
                                attacker_account_id=attacker_acc.id,
                                request_template_json=req_template,
                                expected_secure_result=sug.expected_secure_result,
                                status="generated"
                            )
                            ai_generated_tests.append(ai_tc)
                except Exception as e:
                    write_event(session, scan_id, "planning", f"AI planner error on {ep.path}: {e}", level="warning")
            
            if ai_generated_tests:
                write_event(session, scan_id, "planning", f"AI suggested {len(ai_generated_tests)} additional test cases.")
                test_cases.extend(ai_generated_tests)
        # -------------------------------
        
        if not test_cases:
            write_event(session, scan_id, "planning", "No test cases could be generated. (Do you have endpoints and >= 2 accounts?)", level="warning")
        else:
            for tc in test_cases:
                session.add(tc)
            session.commit()
            write_event(session, scan_id, "planning", f"Generated {len(test_cases)} total test cases.")

        # Phase 6: Executing
        job.phase = "executing"
        job.progress = 80
        write_event(session, scan_id, "executing", f"Executing {len(test_cases)} test cases...")
        session.commit()
        
        from app.http.client import execute_http_request
        from app.models import AuthSession, AuthConfig, TestExecution
        
        # Load auth config
        auth_config = session.exec(select(AuthConfig).where(AuthConfig.project_id == job.project_id)).first()
        
        requests_executed = 0
        max_requests = target_config.max_total_requests
        max_rps = target_config.max_requests_per_second
        delay_between_requests = 1.0 / max_rps if max_rps > 0 else 0
        
        for idx, tc in enumerate(test_cases):
            # Enforce Request Budget
            if requests_executed >= max_requests:
                write_event(session, scan_id, "executing", f"Request budget reached ({max_requests} requests). Stopping execution.", level="warning")
                break
                
            # Fetch token for the attacker account
            attacker_token = None
            if tc.attacker_account_id and auth_config:
                account = session.get(Account, tc.attacker_account_id)
                if account and account.encrypted_secret:
                    # decode password
                    password = base64.b64decode(account.encrypted_secret).decode("utf-8")
                    
                    # do real login
                    login_url = f"{project.base_url.rstrip('/')}/{auth_config.login_endpoint.lstrip('/')}"
                    # QA Demo Fix: Rewrite localhost
                    if "localhost:9000" in login_url or "127.0.0.1:9000" in login_url:
                        login_url = login_url.replace("localhost:9000", "vulnerable-saas:9000").replace("127.0.0.1:9000", "vulnerable-saas:9000")
                        
                    payload = {
                        auth_config.username_field: account.username,
                        auth_config.password_field: password
                    }
                    try:
                        print(f"[DEBUG] Login payload: {payload}")
                        r = httpx.post(login_url, json=payload, timeout=5.0)
                        print(f"[DEBUG] Login to {login_url} returned {r.status_code}: {r.text}")
                        if r.status_code == 200:
                            data = r.json()
                            raw_token = data.get(auth_config.token_json_path)
                            print(f"[DEBUG] Raw token fetched: {raw_token[:10] if raw_token else 'None'}")
                            if raw_token:
                                attacker_token = raw_token
                    except Exception as e:
                        print(f"[DEBUG] Login error: {e}")
                        pass
                        
            headers = {}
            if attacker_token and auth_config and auth_config.header_template:
                headers["Authorization"] = auth_config.header_template.replace("{token}", attacker_token)
                
            req = tc.request_template_json
            
            tc_headers = req.get("headers", {})
            for k, v in tc_headers.items():
                headers[k] = v
            
            is_multistep = req.get("is_multistep", False)
            if is_multistep:
                steps = req.get("steps", [])
                status_code, resp_redacted, duration, error = 0, {}, 0, None
                for step in steps:
                    if requests_executed >= max_requests:
                        break
                        
                    url = f"{project.base_url.rstrip('/')}/{step['path'].lstrip('/')}"
                    st, rp, dur, err = execute_http_request(
                        method=step["method"],
                        url=url,
                        headers=headers,
                        json_body=step.get("body"),
                        params=step.get("query"),
                        target_config=target_config,
                        dry_run=job.dry_run
                    )
                    status_code = st
                    resp_redacted = rp
                    duration += dur
                    requests_executed += 1
                    if delay_between_requests > 0 and not job.dry_run:
                        time.sleep(delay_between_requests)
                    if err:
                        error = err
                        break
            else:
                url = f"{project.base_url.rstrip('/')}/{req['path'].lstrip('/')}"
                status_code, resp_redacted, duration, error = execute_http_request(
                    method=req["method"],
                    url=url,
                    headers=headers,
                    json_body=req.get("body"),
                    params=req.get("query"),
                    target_config=target_config,
                    dry_run=job.dry_run
                )
                requests_executed += 1
                if delay_between_requests > 0 and not job.dry_run:
                    time.sleep(delay_between_requests)
            
            # Save Execution
            execution = TestExecution(
                test_case_id=tc.id,
                scan_id=scan_id,
                status_code=status_code,
                duration_ms=duration,
                error_message=error,
                request_json_redacted=req,
                response_json_redacted=resp_redacted
            )
            session.add(execution)
            
            # Update Test Case Status based on deterministic rules
            if error:
                tc.status = "error"
            elif status_code >= 500:
                tc.status = "error"
            else:
                # Basic suspicious evaluation
                if tc.category == "BFLA" and status_code in [200, 201]:
                    tc.status = "suspicious"
                elif tc.category == "BOLA" and status_code in [200, 201]:
                    tc.status = "suspicious"
                elif tc.category == "MASS_ASSIGNMENT" and status_code in [200, 201]:
                    tc.status = "suspicious"
                elif tc.category == "BUSINESS_LOGIC" and status_code in [200, 201]:
                    tc.status = "suspicious"
                else:
                    tc.status = "passed"
                    
            session.add(tc)
            
            # Update progress
            if idx % max(1, (len(test_cases) // 10)) == 0:
                job.progress = 80 + int((idx / len(test_cases)) * 15)
                session.commit()
                
        # Update target config with actual requests used (for reporting)
        write_event(session, scan_id, "executing", f"Executed {requests_executed} requests total.")
        
        # Phase 7: Verifying
        job.phase = "verifying"
        write_event(session, scan_id, "verifying", "Evaluating test results to confirm findings...")
        session.commit()
        
        # We need all executions for this scan
        stmt = select(TestExecution).where(TestExecution.scan_id == scan_id)
        all_executions = session.exec(stmt).all()
        
        from app.engines.verification import verify_test_cases
        new_findings = verify_test_cases(session, scan_id, job.project_id, test_cases, all_executions, job.ai_enabled)
        
        write_event(session, scan_id, "verifying", f"Verification complete. Created {len(new_findings)} confirmed or suspicious findings.")
        session.commit()

        # Completed
        job.status = "completed"
        job.phase = "reporting"
        job.progress = 100
        job.completed_at = datetime.now(timezone.utc)
        write_event(session, scan_id, "reporting", "Scan completed successfully.")
        session.commit()
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {str(e)}")
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        try:
            write_event(session, scan_id, job.phase, f"Scan failed: {str(e)}", level="error")
            session.commit()
        except:
            session.rollback()


def poll_jobs():
    engine = get_engine()
    if not engine:
        return

    logger.info("Worker polling loop started.")
    
    while True:
        try:
            with Session(engine) as session:
                # Find a pending job and lock it
                stmt = select(ScanJob).where(ScanJob.status == "pending").with_for_update(skip_locked=True)
                job = session.exec(stmt).first()
                
                if job:
                    job.status = "running"
                    job.started_at = datetime.now(timezone.utc)
                    session.commit()
                    
                    process_scan(session, job)
                    
        except Exception as e:
            logger.error(f"Error in polling loop: {e}")
            
        time.sleep(5)


if __name__ == "__main__":
    try:
        poll_jobs()
    except KeyboardInterrupt:
        logger.info("Worker interrupted.")
