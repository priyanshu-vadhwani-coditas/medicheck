from fastapi import FastAPI
from app.api.endpoints import router as v1_router

app = FastAPI(title="MediCheck: AI Insurance Validator for Clinical Summaries")

app.include_router(v1_router, prefix="/api")