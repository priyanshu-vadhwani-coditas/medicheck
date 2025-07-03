# MediCheck: AI Insurance Validator for Clinical Summaries

## Overview
MediCheck is an AI-powered FastAPI service that validates clinical summaries (in JSON format) for insurance approval, using LLMs, LangGraph, and Pydantic for robust, explainable validation.

## Features
- **Guardrail LLM node:** Checks if the uploaded JSON is a clinical summary for insurance. Rejects politely if not.
- **Insurance Policy Validation:** Ensures all mandatory fields are present and flags missing/discrepant data.
- **Bonus:** Suggests what is missing for insurance approval.

## Flow
1. **User uploads a clinical summary JSON** via API (file upload or raw JSON).
2. **Guardrail Node (LLM):** Determines if the file is for insurance. If not, returns a polite rejection.
3. **Validation Node:** Validates against insurance policy (Pydantic model). Flags missing fields/discrepancies and suggests corrections.
4. **Policy Node (LLM):** Checks insurance approval criteria using the policy in `/policy_data/default_policy.py`.
5. **Response:** Structured output with validation and policy results, suggestions, and messages.

## Sample Data & Policy
- See `/policy_data/default_policy.py` for the insurance policy logic used by the agent.
- See `/policy_data/policy_pass_summary.json`, `/policy_data/policy_fail_summary.json`, `/policy_data/validation_fail_summary.json`, and `/policy_data/guardrail_fail_summary.json` for example outputs and summaries.

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
Medicheck Clinical Insurance Policy Checker/
│
├── app/
│   ├── api/
│   │   └── endpoints.py           # FastAPI endpoints
│   ├── flow_graph/
│   │   └── langgraph.py          # LangGraph flow logic
│   ├── models/
│   │   ├── clinical_summary.py   # Pydantic model for summaries
│   │   └── output.py             # Output models
│   ├── prompts/
│   │   ├── guardrail_prompt.py
│   │   ├── policy_eval_prompt.py
│   │   └── validator_suggestion_prompt.py
│   ├── services/
│   │   ├── guardrail.py
│   │   ├── policy.py
│   │   └── validator.py
│   ├── utils/
│   │   └── llm.py                # LLM utility functions
│   ├── static/
│   │   ├── index.html            # (Optional) Web UI
│   │   ├── style.css
│   │   └── script.js
│   └── main.py                   # FastAPI app entrypoint
│
├── policy_data/
│   ├── default_policy.py         # Default insurance policy logic
│   ├── policy_pass_summary.json  # Example: policy pass output
│   ├── policy_fail_summary.json  # Example: policy fail output
│   ├── validation_fail_summary.json # Example: validation fail output
│   └── guardrail_fail_summary.json  # Example: guardrail fail output
│
├── README.md
├── pyproject.toml
└── ...
```
