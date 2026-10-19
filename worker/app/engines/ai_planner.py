import os
import httpx
import json
import logging
from typing import Optional, List, Type, Any
from pydantic import BaseModel

from app.models import (
    EndpointClassification,
    TestCaseSuggestion,
    PayloadMutationSuggestion,
    FindingExplanation
)

logger = logging.getLogger(__name__)

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def prompt_llm_structured(prompt: str, schema_class: Type[BaseModel]) -> Optional[Any]:
    """
    Calls Groq API and requests structured JSON output matching the given Pydantic schema.
    """
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set. Cannot use AI Planner.")
        return None

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    
    schema_json = json.dumps(schema_class.model_json_schema(), indent=2)
    
    # We append instructions to the prompt to force JSON format matching the schema
    full_prompt = f"{prompt}\n\nYou must respond with a JSON object. Ensure the JSON strictly follows this schema:\n{schema_json}"

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        r.raise_for_status()
        data = r.json()
        
        response_text = data["choices"][0]["message"]["content"]
        
        # Parse JSON and validate against schema
        parsed_json = json.loads(response_text)
        return schema_class.model_validate(parsed_json)
    except httpx.HTTPStatusError as e:
        logger.error(f"Groq API returned HTTP {e.response.status_code}: {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.warning(f"Groq API connection error: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Groq API returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Groq API: {e}")
        return None

def classify_endpoint(method: str, path: str, tags: list, params: list, body_schema: dict) -> Optional[EndpointClassification]:
    prompt = f"""
    You are a professional API security tester. Please classify the following API endpoint based on its business context and sensitivity.
    Do not generate any tests yet. Just provide a structured classification.
    
    Endpoint: {method} {path}
    Tags: {tags}
    Parameters: {params}
    Body Schema: {body_schema}
    """
    return prompt_llm_structured(prompt, EndpointClassification)

# We use a wrapper model for a list of suggestions since JSON format expects a single root object schema
class TestCaseList(BaseModel):
    tests: List[TestCaseSuggestion]

def suggest_test_cases(method: str, path: str, classification: EndpointClassification, roles: list) -> List[TestCaseSuggestion]:
    prompt = f"""
    You are an expert security tester. Based on the endpoint classification below, suggest specific security test cases.
    Focus ONLY on BOLA (Broken Object Level Authorization), BFLA (Broken Function Level Authorization), and Mass Assignment.
    
    Endpoint: {method} {path}
    Roles available: {roles}
    Classification:
    - Area: {classification.business_area}
    - Sensitivity: {classification.sensitivity}
    - Potential vulnerabilities: {classification.possible_vulnerabilities}
    
    Suggest test cases to verify these vulnerabilities. Provide realistic scenarios and clearly state the expected secure result.
    Do NOT suggest destructive attacks or tests that delete data.
    """
    result = prompt_llm_structured(prompt, TestCaseList)
    if result:
        return result.tests
    return []

def explain_finding(title: str, category: str, description: str, method: str, path: str) -> Optional[FindingExplanation]:
    prompt = f"""
    You are a professional application security engineer writing a report for developers.
    Provide a clear explanation of this vulnerability, its impact, and how to remediate it.
    
    Title: {title}
    Category: {category}
    Endpoint: {method} {path}
    Context: {description}
    """
    return prompt_llm_structured(prompt, FindingExplanation)
