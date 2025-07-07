PDF_EXTRACTION_PROMPT = """
You are an expert at extracting structured clinical summaries from unstructured medical documents.
Given the following text extracted from a PDF, identify and extract the clinical summary in JSON format.
If information is missing, do not include the field in the JSON.

PDF Text:
{pdf_text}

Return your answer in the following JSON format (replace the descriptions with actual values from the PDF):

{example_json}
""" 