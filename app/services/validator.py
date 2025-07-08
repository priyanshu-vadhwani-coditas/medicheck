from typing import List, Dict, Any
from app.utils.llm import GroqLLM
from app.prompts.validator_suggestion_prompt import VALIDATOR_SUGGESTION_PROMPT
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from app.models.output import ValidatorOutput
from policy_data.example_json import SAMPLE
import json

def validate_clinical_summary(data: dict) -> Dict[str, Any]:
    """
    Validates clinical summary using LLM-based validation instead of hardcoded Pydantic validation.
    This provides more intelligent and flexible validation that considers business logic.
    """
    try:
        llm = GroqLLM(model="llama3-70b-8192", temperature=0.1)
        
        base_parser = PydanticOutputParser(pydantic_object=ValidatorOutput)
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
        
        prompt = VALIDATOR_SUGGESTION_PROMPT.format(
            data=json.dumps(data, indent=2),
            example_json=json.dumps(SAMPLE, indent=2)
        ) + "\n" + parser.get_format_instructions()
        
        llm_response = llm.call(prompt)
        
        result = parser.parse(llm_response)
        return result.dict()
        
    except Exception as e:
        missing_fields = []
        suggestions = []
        
        required_fields = [
            "patient_demographics.full_name",
            "patient_demographics.age", 
            "patient_demographics.gender",
            "patient_demographics.insurance_id",
            "hpi.chief_complaint",
            "hpi.duration",
            "hpi.onset", 
            "hpi.associated_symptoms",
            "hpi.documentation_date",
            "diagnosis_discharge_summary.final_diagnosis",
            "diagnosis_discharge_summary.icd_10_code",
            "diagnosis_discharge_summary.treatment_summary",
            "diagnosis_discharge_summary.discharge_plan",
            "physician_signature.attending_physician",
            "physician_signature.date_of_report",
            "physician_signature.digital_signature"
        ]
        
        for field_path in required_fields:
            field_parts = field_path.split('.')
            current = data
            field_exists = True
            
            for part in field_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    field_exists = False
                    break
            
            if not field_exists or (isinstance(current, str) and not current.strip()) or (isinstance(current, list) and len(current) == 0):
                missing_fields.append(field_path)
        
        if not data.get("procedures_treatments") or len(data["procedures_treatments"]) == 0:
            missing_fields.append("procedures_treatments")
        if not data.get("imaging_lab_results") or len(data["imaging_lab_results"]) == 0:
            missing_fields.append("imaging_lab_results")
        
        if missing_fields:
            suggestions.append(f"Missing required fields: {', '.join(missing_fields)}. Please provide complete information for all required fields.")
            is_valid = False
        else:
            suggestions.append("All required fields appear to be present.")
            is_valid = True
        
        return {
            "is_valid": is_valid,
            "missing_fields": missing_fields,
            "suggestions": suggestions
        } 