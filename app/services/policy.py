from typing import Dict, Any, Optional
from app.utils.llm import GroqLLM
import json
from app.prompts.policy_eval_prompt import POLICY_EVAL_PROMPT
from policy_data.default_policy import INSURANCE_POLICY
from app.models.output import PolicyEvalOutput
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

def evaluate_policy(data: Dict[str, Any], policy: Optional[str] = None) -> Dict[str, Any]:
    """
    Uses an LLM to evaluate if the provided clinical summary data meets the insurance policy criteria.
    Returns a dictionary with the evaluation result and a user-friendly message.
    """
    if policy is None:
        policy = INSURANCE_POLICY
    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    base_parser = PydanticOutputParser(pydantic_object=PolicyEvalOutput)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
    prompt = POLICY_EVAL_PROMPT.format(
        policy=policy,
        patient_json=json.dumps(data, indent=2)
    ) + "\n" + parser.get_format_instructions()

    response = llm.call(prompt)
    try:
        result = parser.parse(response)
        return result.dict()
    except Exception:
        return {
            "policy_approved": False,
            "failed_criteria": ["LLM response could not be parsed as JSON."],
            "policy_message": "Sorry, we could not determine insurance eligibility. Please check your data and policy."
        } 