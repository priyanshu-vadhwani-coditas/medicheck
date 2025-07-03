from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Any, Optional
import json
from app.flow_graph.langgraph import process_clinical_summary

router = APIRouter()

@router.post(
    "/validate-summary-stream",
    summary="Validate a clinical summary JSON file or object (streaming)",
    response_description="Validation result streamed as a user-friendly message."
)
async def validate_summary_stream(
    file: UploadFile = File(None, description="A JSON file containing the clinical summary."),
    request: Request = None
):
    """
    Validate a clinical summary for insurance using AI and schema checks.
    Streams a user-friendly message about the summary's validity and suggestions for improvement.
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

    # Run the flow and get the final_response (which may be markdown)
    result = process_clinical_summary(data)
    message = result["message"]
    def stream_message():
        for token in message:
            yield token
    return StreamingResponse(stream_message(), media_type="text/plain") 