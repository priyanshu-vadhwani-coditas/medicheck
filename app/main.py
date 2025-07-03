from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import router as v1_router

app = FastAPI(title="MediCheck: AI Insurance Validator for Clinical Summaries")

app.include_router(v1_router, prefix="/api")
app.mount("/static", StaticFiles(directory="app/static"), name="static") 