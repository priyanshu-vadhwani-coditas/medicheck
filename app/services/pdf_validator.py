import fitz
from app.utils.llm import GroqLLM
from app.prompts.pdf_extraction_prompt import PDF_EXTRACTION_PROMPT
from app.models.clinical_summary import ClinicalSummary
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
import json
from policy_data.example_json import SAMPLE

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_clinical_summary_from_pdf(pdf_path: str):
    """
    Extracts clinical summary JSON from a PDF using LLM and a custom prompt.
    Returns the parsed ClinicalSummary object or a polite error message.
    """
    try:
        pdf_text = extract_text_from_pdf(pdf_path)
        print(pdf_text)
    except Exception as e:
        return {"polite_message": f"Failed to extract text from PDF: {str(e)}"}

    llm = GroqLLM(model="llama3-70b-8192", temperature=0.2)
    base_parser = PydanticOutputParser(pydantic_object=ClinicalSummary)
    parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm.llm)
    prompt = PDF_EXTRACTION_PROMPT.format(
        pdf_text=pdf_text,
        example_json=json.dumps(SAMPLE, indent=2)
    ) + "\n" + parser.get_format_instructions()
    response = llm.call(prompt)
    try:
        result = parser.parse(response)
        return result.dict()
    except Exception:
        return {"polite_message": "Sorry, we could not extract a valid clinical summary from your PDF. Please check your file and try again."}
