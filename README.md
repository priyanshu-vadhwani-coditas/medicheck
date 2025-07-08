# MediCheck: AI Insurance Validator for Clinical Summaries

## Overview
MediCheck is an AI-powered clinical summary validation system that uses LLMs, LangGraph, and intelligent validation to assess clinical summaries for insurance approval. The system supports both JSON and PDF inputs, provides comprehensive validation, and generates patient summaries with professional PDF reports.

## Features
- **📄 PDF Support**: Extract and validate clinical summaries from PDF documents
- **🔍 LLM-Based Validation**: Intelligent validation using LLM instead of rigid Pydantic models
- **🛡️ Guardrail System**: AI determines if documents are valid clinical summaries for insurance
- **📋 Summary Generation**: Generate structured patient summaries with markdown formatting
- **📊 Policy Evaluation**: Check against insurance approval criteria
- **📄 PDF Reports**: Download professional validation reports and summaries
- **🎨 Streamlit UI**: User-friendly web interface for easy interaction

## Flow
1. **Upload**: User uploads a clinical summary JSON file or PDF document
2. **PDF Extraction** (if PDF): AI extracts structured data from PDF using LLM
3. **Guardrail Check**: AI determines if the document is a valid clinical summary for insurance
4. **Field Validation**: LLM validates required fields and data quality against example structure
5. **Policy Evaluation**: AI checks against insurance approval criteria
6. **Summary Generation** (optional): Generate patient summary with markdown formatting
7. **Report Download**: Download validation results and summaries as professional PDFs

## Validation Outcomes
- ✅ **Approved**: All validation checks passed successfully
- ⚠️ **Validation Warning**: Missing fields or data quality issues detected
- ❌ **Policy Rejected**: Valid summary but doesn't meet insurance policy criteria
- 📝 **Guardrail Failed**: Document not recognized as a clinical summary

## Running the Project

### Option 1: Streamlit UI (Recommended)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Start the Streamlit UI:
   ```bash
   streamlit run app/ui/app.py
   ```
4. Open your browser to `http://localhost:8501`

### Option 2: API Only
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Use the API endpoints:
   - `POST /api/validate-summary` - Validate JSON clinical summary
   - `POST /api/upload-pdf` - Extract and validate PDF clinical summary
   - `POST /api/summary` - Generate patient summary

## API Endpoints

### Validate JSON Summary
```bash
POST /api/validate-summary
Content-Type: application/json

{
  "patient_demographics": {...},
  "hpi": {...},
  ...
}
```

### Upload and Validate PDF
```bash
POST /api/upload-pdf
Content-Type: multipart/form-data

file: [PDF file]
```

### Generate Summary
```bash
POST /api/summary
Content-Type: application/json

{
  "patient_demographics": {...},
  ...
}
```

## Project Structure
```
Medicheck Clinical Insurance Policy Checker/
│
├── app/
│   ├── api/
│   │   └── endpoints.py              # FastAPI endpoints
│   ├── flow_graph/
│   │   └── langgraph.py             # LangGraph flow with debug statements
│   ├── models/
│   │   ├── clinical_summary.py      # Pydantic models
│   │   └── output.py                # Output models
│   ├── prompts/
│   │   ├── guardrail_prompt.py      # Guardrail validation prompt
│   │   ├── policy_eval_prompt.py    # Policy evaluation prompt
│   │   ├── validator_suggestion_prompt.py  # LLM-based validation prompt
│   │   ├── pdf_extraction_prompt.py # PDF extraction prompt
│   │   └── summary_prompt.py        # Summary generation prompt
│   ├── services/
│   │   ├── guardrail.py             # Guardrail service
│   │   ├── policy.py                # Policy evaluation service
│   │   ├── validator.py             # LLM-based validation service
│   │   ├── pdf_validator.py         # PDF extraction service
│   │   └── summary.py               # Summary generation service
│   ├── ui/
│   │   └── app.py                   # Streamlit UI application
│   ├── utils/
│   │   └── llm.py                   # LLM utility functions
│   └── main.py                      # FastAPI app entrypoint
│
├── policy_data/
│   ├── default_policy.py            # Insurance policy logic
│   ├── example_json.py              # Example JSON structure
│   ├── policy_pass_summary.json     # Example: policy pass output
│   ├── policy_fail_summary.json     # Example: policy fail output
│   ├── validation_fail_summary.json # Example: validation fail output
│   └── guardrail_fail_summary.json  # Example: guardrail fail output
│
├── README.md
├── requirements.txt                  # Python dependencies
├── pyproject.toml                   # Poetry configuration
└── ...
```

## Key Technologies
- **FastAPI**: High-performance web framework for APIs
- **Streamlit**: Web interface for easy interaction
- **LangGraph**: Workflow orchestration and state management
- **Groq LLM**: Fast and reliable language model for validation
- **PyMuPDF**: PDF text extraction and processing
- **ReportLab**: Professional PDF report generation
- **Pydantic**: Data validation and serialization

## Dependencies
All required dependencies are listed in `requirements.txt`:
- FastAPI, Uvicorn for API server
- Streamlit for web interface
- LangChain, LangGraph for AI workflows
- PyMuPDF for PDF processing
- ReportLab for PDF generation
- Markdown libraries for text formatting

## Development
The project uses Poetry for dependency management in development:
```bash
poetry install
poetry run uvicorn app.main:app --reload
poetry run streamlit run app/ui/app.py
```
