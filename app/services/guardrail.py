import json
from app.utils.llm import GroqLLM
from app.prompts.guardrail_prompt import GUARDRAIL_PROMPT
from app.models.output import GuardrailOutput
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

async def check_is_insurance_summary(json_data: dict) -> dict:
    """
    Uses an LLM to determine if the provided JSON data represents a clinical summary intended for insurance approval.
    Returns a dictionary with the result and a polite message if not valid.
    Now async for better performance.
    """
    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    base_parser = PydanticOutputParser(pydantic_object=GuardrailOutput)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
    prompt = GUARDRAIL_PROMPT.format(json_data=json.dumps(json_data, indent=2)) + "\n" + parser.get_format_instructions()
    # Get the output from the LLM asynchronously
    response = await llm.acall(prompt)
    try:
        result = parser.parse(response)
        return result.dict()
    except Exception:
        # If parsing fails, return a default polite message
        return {
            "is_insurance_summary": False,
            "reason": "LLM response could not be parsed as JSON.",
            "polite_message": "Sorry, we could not determine if your document is a clinical summary for insurance. Please check your file and try again."
        } 