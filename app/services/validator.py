from typing import List, Dict, Any
from pydantic import ValidationError
from app.models.clinical_summary import ClinicalSummary

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
        suggestions = []
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            missing_fields.append(loc)
            suggestions.append(f"Field '{loc}' is missing or invalid: {err['msg']}")
        return {
            "is_valid": False,
            "missing_fields": missing_fields,
            "suggestions": suggestions
        } 