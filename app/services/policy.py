from typing import Dict, Any, Optional
from app.utils.llm import GroqLLM
import json
import os
import re
from app.prompts.policy_eval_prompt import POLICY_EVAL_PROMPT
from policy_data.default_policy import INSURANCE_POLICY

def extract_first_json(text: str) -> str:
    print("[DEBUG] extract_first_json input:\n", text)
    match = re.search(r"\{[\s\S]*?\}", text)
    if match:
        print("[DEBUG] extract_first_json extracted JSON:\n", match.group(0))
        return match.group(0)
    print("[ERROR] extract_first_json: No JSON object found in LLM response.")
    raise ValueError("No JSON object found in LLM response.")

def evaluate_policy(data: Dict[str, Any], policy: Optional[str] = None) -> Dict[str, Any]:
    if policy is None:
        policy = INSURANCE_POLICY
    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    prompt = POLICY_EVAL_PROMPT.format(
        policy=policy,
        patient_json=json.dumps(data, indent=2)
    )
    print("[DEBUG] Policy prompt:\n", prompt)
    response = llm.invoke(prompt)
    print("[DEBUG] Policy LLM raw response:\n", response)
    try:
        json_str = extract_first_json(response)
        result = json.loads(json_str)
    except Exception as e:
        print("[ERROR] Failed to extract/parse policy LLM response as JSON:", e)
        result = {
            "policy_approved": False,
            "failed_criteria": ["LLM response could not be parsed as JSON."],
            "policy_message": "Sorry, we could not determine insurance eligibility. Please check your data and policy."
        }
    return result 