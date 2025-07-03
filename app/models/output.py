from pydantic import BaseModel

class GuardrailOutput(BaseModel):
    is_insurance_summary: bool
    reason: str
    polite_message: str

class PolicyEvalOutput(BaseModel):
    policy_approved: bool
    failed_criteria: list[str]
    policy_message: str

class ValidatorOutput(BaseModel):
    is_valid: bool
    missing_fields: list[str]
    suggestions: list[str] 