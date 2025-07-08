import fitz
import asyncio
from app.utils.llm import GroqLLM
from app.prompts.pdf_extraction_prompt import PDF_EXTRACTION_PROMPT
from app.models.clinical_summary import ClinicalSummary
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
import json
from policy_data.example_json import SAMPLE

async def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using PyMuPDF.
    Now async to avoid blocking the event loop.
    """
    def _extract_text():
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    # Run the synchronous PDF extraction in a thread pool
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _extract_text)
    return text


async def extract_clinical_summary_from_pdf(pdf_path: str):
    """
    Extracts clinical summary JSON from a PDF using LLM and a custom prompt.
    Returns the parsed ClinicalSummary object or a polite error message.
    Optimized to use a single async LLM call instead of two separate calls.
    """
    try:
        pdf_text = await extract_text_from_pdf(pdf_path)
        print(f"[DEBUG] PDF TEXT EXTRACTED: {pdf_text[:500]}...")
    except Exception as e:
        print(f"[DEBUG] PDF TEXT EXTRACTION ERROR: {e}")
        return {"polite_message": f"Failed to extract text from PDF: {str(e)}"}

    # Create LLM instance once
    llm = GroqLLM(model="llama-3.3-70b-versatile", temperature=0.2)
    
    # Create parser for structured output
    base_parser = PydanticOutputParser(pydantic_object=ClinicalSummary)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
    
    # Combine the prompt with parser instructions in a single call
    prompt = PDF_EXTRACTION_PROMPT.format(
        pdf_text=pdf_text,
        example_json=json.dumps(SAMPLE, indent=2)
    )
    
    print(f"[DEBUG] LLM PROMPT: {prompt[:1000]}...")
    
    # Add parser instructions to the same prompt
    full_prompt = prompt + "\n" + parser.get_format_instructions()
    
    # Single async LLM call instead of two
    response = await llm.acall(full_prompt)
    
    print(f"[DEBUG] LLM RAW RESPONSE: {response}")
    
    # Check if response indicates it's not a clinical summary
    if "polite_message" in response.lower() or "routine medical note" in response.lower() or "not intended for insurance" in response.lower():
        print(f"[DEBUG] LLM RESPONSE INDICATES NON-CLINICAL SUMMARY")
        return {"polite_message": "This document appears to be a routine medical note/checkup and is not intended for insurance approval. Please upload a clinical summary document that includes detailed medical information for insurance purposes."}
    
    # Try to parse the response
    try:
        result = parser.parse(response)
        print(f"[DEBUG] PARSED RESULT: {result}")
        return result.dict()
    except Exception as e:
        print(f"[DEBUG] PARSING ERROR: {e}")
        return {"polite_message": "Sorry, we could not extract a valid clinical summary from your PDF. Please check your file and try again."}
