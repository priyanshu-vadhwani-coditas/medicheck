from typing import List, Dict, Any
from pydantic import ValidationError
from app.models.clinical_summary import ClinicalSummary
from app.utils.llm import GroqLLM
from app.prompts.validator_suggestion_prompt import VALIDATOR_SUGGESTION_PROMPT
import json

def validate_clinical_summary(data: dict) -> Dict[str, Any]:
    try:
        ClinicalSummary.model_validate(data)
        return {
            "is_valid": True,
            "missing_fields": [],
            "suggestions": []
        }
    except ValidationError as e:
        missing_fields = []
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            missing_fields.append(loc)
        # Use LLM to generate a user-friendly suggestion
        llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
        prompt = VALIDATOR_SUGGESTION_PROMPT.format(
            data=json.dumps(data, indent=2),
            missing_fields=missing_fields
        )
        llm_suggestion = llm.invoke(prompt)
        return {
            "is_valid": False,
            "missing_fields": missing_fields,
            "suggestions": [llm_suggestion.strip()]
        } 