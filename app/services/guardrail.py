import json
import re
from app.utils.llm import GroqLLM
from app.prompts.guardrail_prompt import GUARDRAIL_PROMPT

def extract_first_json(text: str) -> str:
    """Extract the first JSON object from a string."""
    print("[DEBUG] extract_first_json input:\n", text)
    match = re.search(r"\{[\s\S]*?\}", text)
    if match:
        print("[DEBUG] extract_first_json extracted JSON:\n", match.group(0))
        return match.group(0)
    print("[ERROR] extract_first_json: No JSON object found in LLM response.")
    raise ValueError("No JSON object found in LLM response.")

def check_is_insurance_summary(json_data: dict) -> dict:
    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    prompt = GUARDRAIL_PROMPT.format(json_data=json.dumps(json_data, indent=2))
    print("[DEBUG] Guardrail prompt:\n", prompt)
    response = llm.invoke(prompt)
    print("[DEBUG] Guardrail LLM raw response:\n", response)
    try:
        json_str = extract_first_json(response)
        result = json.loads(json_str)
    except Exception as e:
        print("[ERROR] Failed to extract/parse guardrail LLM response as JSON:", e)
        result = {
            "is_insurance_summary": False,
            "reason": "LLM response could not be parsed as JSON.",
            "polite_message": "Sorry, we could not determine if your document is a clinical summary for insurance. Please check your file and try again."
        }
    return result 