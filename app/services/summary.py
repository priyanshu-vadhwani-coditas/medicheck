import json
from app.utils.llm import GroqLLM
from app.prompts.summary_prompt import SUMMARY_GENERATOR_PROMPT

async def summary_generator(json_data: dict) -> str:
    """
    Uses an LLM to generate a summary (about 250 words) based on the provided JSON data. Returns the summary as a string.
    Now async for better performance.
    """
    llm = GroqLLM(model="llama-3.3-70b-versatile", temperature=0.2)
    prompt = SUMMARY_GENERATOR_PROMPT.format(json_data=json.dumps(json_data,indent=2))
    print(f"[DEBUG] SUMMARY LLM PROMPT: {prompt[:1000]}...")
    response = await llm.acall(prompt)
    print(f"[DEBUG] SUMMARY LLM RAW RESPONSE: {response}")
    return response