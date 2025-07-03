from typing import List, Dict, Any
from pydantic import ValidationError
from app.models.clinical_summary import ClinicalSummary
from app.utils.llm import GroqLLM
from app.prompts.validator_suggestion_prompt import VALIDATOR_SUGGESTION_PROMPT
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from app.models.output import ValidatorOutput
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
        # Use LLM to generate a user-friendly suggestion with output parsing
        llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
        base_parser = PydanticOutputParser(pydantic_object=ValidatorOutput)
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
        prompt = VALIDATOR_SUGGESTION_PROMPT.format(
            data=json.dumps(data, indent=2),
            missing_fields=missing_fields
        ) + "\n" + parser.get_format_instructions()
        llm_response = llm.call(prompt)
        try:
            result = parser.parse(llm_response)
            return result.dict()
        except Exception:
            return {
                "is_valid": False,
                "missing_fields": missing_fields,
                "suggestions": ["Sorry, we could not generate suggestions. Please check your data."]
            } 