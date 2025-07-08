import json
from app.utils.llm import GroqLLM
from app.prompts.summary_prompt import SUMMARY_GENERATOR_PROMPT

async def summary_generator(json_data: dict) -> str:
    """
    Uses an LLM to generate a summary (about 250 words) based on the provided JSON data. Returns the summary as a string.
    Now async for better performance.
    """
    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    prompt = SUMMARY_GENERATOR_PROMPT.format(json_data=json.dumps(json_data,indent=2))
    
    response = await llm.acall(prompt)
    return response