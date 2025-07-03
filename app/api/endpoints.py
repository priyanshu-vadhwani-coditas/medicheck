from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any
import json
from app.graph_flow.langgraph_flow import process_clinical_summary

router = APIRouter()

@router.post("/validate-summary")
async def validate_summary(
    file: UploadFile = File(None),
    request: Request = None
):
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

    result = process_clinical_summary(data)
    return JSONResponse(content=result) 