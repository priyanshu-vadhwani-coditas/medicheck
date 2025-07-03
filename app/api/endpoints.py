from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Optional
import json
from app.flow_graph.langgraph import process_clinical_summary

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