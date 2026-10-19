export interface Project {
  id: string;
  name: string;
  description: string | null;
  base_url: string;
  environment_type: "local" | "lab" | "staging" | "bug_bounty";
  mode: string;
  created_at: string;
  updated_at: string;
}

export interface TargetConfig {
  id: string;
  project_id: string;
  allowed_hosts: string[];
  allowed_paths: string[];
  forbidden_paths: string[];
  max_requests_per_second: number;
  max_total_requests: number;
  allow_destructive_tests: boolean;
  allow_delete_requests: boolean;
  allow_payment_tests: boolean;
  selected_wordlist: string | null;
}

export interface ApiError {
  message: string;
  status?: number;
}

export interface UploadedSpec {
  id: string;
  project_id: string;
  source_type: "file" | "url";
  original_filename: string | null;
  source_url: string | null;
  parsed_successfully: boolean;
  parse_error: string | null;
  created_at: string;
}

export interface Endpoint {
  id: string;
  project_id: string;
  spec_id: string;
  method: string;
  path: string;
  operation_id: string | null;
  summary: string | null;
  description: string | null;
  tags: string[];
  auth_required: boolean;
  path_params: string[];
  query_params: string[];
  body_fields: string[];
  sensitive_score: number;
  sensitive_reasons: string[];
  created_at: string;
}

export interface EndpointDetail extends Endpoint {
  parameters_json: any;
  request_schema_json: any;
  response_schema_json: any;
}

export interface Role {
  id: string;
  project_id: string;
  name: string;
  level: number;
  description: string | null;
  created_at: string;
}

export interface Account {
  id: string;
  project_id: string;
  role_id: string | null;
  label: string;
  username: string;
  auth_type: string;
  notes: string | null;
  created_at: string;
  has_secret: boolean;
  role_name: string | null;
  login_status: "success" | "error" | null;
  last_login_at: string | null;
}

export interface AuthConfig {
  id: string;
  project_id: string;
  auth_type: string;
  login_endpoint: string | null;
  method: string;
  username_field: string;
  password_field: string;
  token_json_path: string;
  header_template: string;
  refresh_endpoint: string | null;
}

export interface LoginTestResult {
  account_id: string;
  account_label: string;
  success: boolean;
  masked_token: string | null;
  error: string | null;
}

export interface ScanJob {
  id: string;
  project_id: string;
  status: "created" | "pending" | "running" | "completed" | "failed" | "cancelled";
  phase: string;
  progress: number;
  ai_enabled: boolean;
  safety_profile: string;
  options_json: any | null;
  roe_confirmed: boolean;
  roe_confirmed_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ScanEvent {
  id: string;
  scan_id: string;
  level: "info" | "warning" | "error";
  phase: string;
  message: string;
  data_json: any | null;
  created_at: string;
}

export interface ScanCreateRequest {
  ai_enabled: boolean;
  safety_profile: string;
  options_json?: any;
  roe_confirmed: boolean;
}

export interface Evidence {
  id: string;
  finding_id: string;
  request_method: string;
  request_url: string;
  request_headers_redacted: any | null;
  request_body_redacted: any | null;
  response_status: number;
  response_headers_redacted: any | null;
  response_body_redacted: any | null;
  proof_text: string;
  before_state_json: any | null;
  after_state_json: any | null;
  created_at: string;
}

export interface Finding {
  id: string;
  project_id: string;
  scan_id: string;
  test_case_id: string;
  title: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: "confirmed" | "likely" | "suspicious";
  endpoint_method: string;
  endpoint_path: string;
  attacker_role: string | null;
  victim_role: string | null;
  status: "open" | "accepted" | "false_positive" | "fixed";
  description: string;
  impact: string;
  remediation: string;
  created_at: string;
  evidence?: Evidence;
}
