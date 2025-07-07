from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Optional
import json
from app.flow_graph.langgraph import process_clinical_summary
import aiofiles
import uuid
from app.services.summary import summary_generator

router = APIRouter()

@router.post(
    "/validate-summary",
    summary="Validate a clinical summary JSON file or object",
    response_description="Validation result as a user-friendly message."
)
async def validate_summary(
    file: UploadFile = File(None, description="A JSON file containing the clinical summary."),
    request: Request = None
):
    """
    Validate a clinical summary for insurance using AI and schema checks.
    Returns a user-friendly message about the summary's validity and suggestions for improvement as JSON.
    """
    if file:
        if not file.content_type or not file.content_type.endswith("json"):
            raise HTTPException(status_code=400, detail="Uploaded file must be a JSON file.")
        try:    
            contents = await file.read()
            data = json.loads(contents)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON file.")
    else:
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    # Run the flow and get the full final state (all details)
    result = process_clinical_summary(data)
    return JSONResponse(result)

@router.post(
    "/upload-pdf",
    summary="Upload a PDF and extract clinical summary",
    response_description="Extracted clinical summary and validation results."
)
async def upload_pdf(
    file: UploadFile = File(..., description="A PDF file containing the clinical summary.")
):
    """
    Accepts a PDF file, extracts the clinical summary using LLM, and returns the result.
    """
    if not file.content_type or not file.content_type.endswith("pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")
    temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
    try:
        async with aiofiles.open(temp_filename, 'wb') as out_file:
            contents = await file.read()
            await out_file.write(contents)
        result = process_clinical_summary(pdf_path=temp_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        import os
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    return JSONResponse(result)

@router.post(
    "/summary",
    summary="Generate a 250-word summary for a clinical summary JSON",
    response_description="A concise summary for the patient."
)
async def generate_summary(request: Request):
    """
    Generate a summary for the given clinical summary JSON using the LLM.
    Returns a 250-word summary as a string.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    summary = summary_generator(data)
    return {"summary": summary} 