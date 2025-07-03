# MediCheck: AI Validator for Clinical Summaries

## Overview
MediCheck is an AI-powered FastAPI service that validates clinical summaries (in JSON format) for insurance approval, using LLMs, LangGraph, and Pydantic for robust, explainable validation.

## Features
- Guardrail LLM node: Checks if the uploaded JSON is a clinical summary for insurance. Rejects politely if not.
- Insurance Policy Validation: Ensures all mandatory fields are present and flags missing/discrepant data.
- Bonus: Suggests what is missing for insurance approval.

## Flow
1. **User uploads a clinical summary JSON** via API (file upload or raw JSON).
2. **Guardrail Node (LLM):** Determines if the file is for insurance. If not, returns a polite rejection.
3. **Validation Node:** Validates against insurance policy (Pydantic model). Flags missing fields/discrepancies and suggests corrections.
4. **Policy Node (LLM):** Checks insurance approval criteria using the policy in `/policy_Data/default_policy.txt`.
5. **Response:** Structured output with validation and policy results, suggestions, and messages.

## Sample JSON & Policy
- See `policy_Data/sample_clinical_summary.json` for a valid example.
- See `policy_Data/default_policy.txt` for the insurance policy used by the agent.

## Running the Project
1. Install dependencies with Poetry:
   ```bash
   poetry install
   ```
2. Start the FastAPI server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
3. Use the `/api/validate-summary` endpoint to upload your clinical summary JSON.
   - **File upload:**
     - `POST /api/validate-summary` with `multipart/form-data` (key: `file`)
   - **Raw JSON:**
     - `POST /api/validate-summary` with `application/json` body

## Project Structure
```
Clinical_Summary_Generator/
│
├── app/
│   ├── api/
│   │   └── endpoints.py         # FastAPI endpoints
│   ├── graph_flow/             # LangGraph flow logic
│   ├── models/                 # Pydantic models
│   ├── prompts/                # LLM prompts
│   ├── services/               # LLM, validation, policy logic
│   └── utils/                  # Utility functions (LLM, etc.)
│   └── main.py                 # FastAPI app entrypoint
│
├── policy_Data/
│   ├── default_policy.txt      # Default insurance policy
│   └── sample_clinical_summary.json # Example clinical summary
│
├── README.md
├── pyproject.toml
└── ...
```
