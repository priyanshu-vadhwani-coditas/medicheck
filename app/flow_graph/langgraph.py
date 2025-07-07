import os
from typing import Dict, Any, TypedDict, List
from typing_extensions import TypedDict
import json
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from app.services.guardrail import check_is_insurance_summary
from app.services.validator import validate_clinical_summary
from app.services.policy import evaluate_policy
from app.services.pdf_validator import extract_clinical_summary_from_pdf

load_dotenv()


class AgentState(TypedDict):
    """
    Represents the state passed between nodes in the validation flow.
    """
    input_json: Dict[str, Any]  
    pdf_path: str  
    is_insurance_summary: bool
    is_valid: bool
    missing_fields: List[str]
    suggestions: List[str]
    policy_approved: bool
    failed_criteria: List[str]
    final_response: str

def guardrail_node(state: AgentState) -> AgentState:
    """
    Node: Checks if the input JSON or pdf is a valid insurance summary using the LLM guardrail.
    """
    print("Enteringg guardrail_node")
    result = check_is_insurance_summary(state["input_json"])
    state["is_insurance_summary"] = result.get("is_insurance_summary", False)
    if state["is_insurance_summary"] == False:
        state["final_response"] = result.get("polite_message")
    return state

def validation_node(state: AgentState) -> AgentState:
    """
    Node: Validates the clinical summary fields and provides LLM-generated suggestions if invalid.
    """
    print("Enteringg validation_node")
    result = validate_clinical_summary(state["input_json"])
    state["is_valid"] = result["is_valid"]
    state["missing_fields"] = result["missing_fields"]
    state["suggestions"] = result["suggestions"]
    if not state["is_valid"]:
        if result["suggestions"]:
            state["final_response"] = " ".join(result["suggestions"])
        else:
            state["final_response"] = "Clinical summary is missing required fields."
    return state

def policy_node(state: AgentState) -> AgentState:
    """
    Node: Evaluates the clinical summary against the insurance policy using the LLM.
    """
    print("Enteringg policy_node")
    result = evaluate_policy(state["input_json"])
    state["policy_approved"] = result["policy_approved"]
    state["failed_criteria"] = result["failed_criteria"]
    state["final_response"] = result["policy_message"]
    return state

def pdf_extraction_node(state: AgentState) -> AgentState:
    """
    """
    print("Enteringg pdf_extraction_node")
    result = extract_clinical_summary_from_pdf(state["pdf_path"])
    if "polite_message" not in result:
        state["input_json"] = result
        state["final_response"] = "PDF extraction successful."
    else:
        state["final_response"] = result.get("polite_message", "Unknown PDF extraction error.")
    return state

def input_router(state: AgentState) -> str:
    """
    Router: Decides whether to process JSON or PDF input.
    """
    print("Enteringg input_router")
    if state.get("pdf_path"):
        return "pdf_extraction"
    else:
        return "guardrail"

def guardrail_router(state: AgentState) -> str:
    """
    Router: Decides whether to proceed to validation or end if not an insurance summary.
    """
    print("Enteringg guardrail_router")
    if state["is_insurance_summary"] == False:
        return END
    else:
        return "validation"

def validation_router(state: AgentState) -> str:
    """
    Router: Decides whether to proceed to policy evaluation or end if validation fails.
    """
    print("Enteringg validation_router")
    if state["is_valid"] == True:
        return "policy"
    else:
        return END

def create_validation_flow() -> StateGraph:
    """
    Constructs the validation flow graph with guardrail, validation, and policy nodes, and PDF extraction.
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("pdf_extraction", pdf_extraction_node)
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("policy", policy_node)

    workflow.add_conditional_edges(
        START,
        input_router,
        {
            "pdf_extraction": "pdf_extraction",
            "guardrail": "guardrail"
        }
    )
    workflow.add_edge("pdf_extraction", "guardrail")
    workflow.add_conditional_edges(
        "guardrail",
        guardrail_router,
        {
            END: END,
            "validation": "validation"
        }
    )
    workflow.add_conditional_edges(
        "validation",
        validation_router,
        {
            "policy": "policy",
            END: END
        }
    )
    workflow.add_edge("policy", END)
    return workflow.compile()

def process_clinical_summary(input_json: Dict[str, Any] = None, pdf_path: str = None) -> Dict[str, Any]:
    """
    Orchestrates the validation flow for a clinical summary JSON or PDF.
    Returns the full final state with all details for frontend handling.
    """
    flow = create_validation_flow()
    initial_state: AgentState = {
        "input_json": input_json,
        "pdf_path": pdf_path,
        "is_insurance_summary": False,
        "is_valid": False,
        "missing_fields": [],
        "suggestions": [],
        "policy_approved": False,
        "failed_criteria": [],
        "final_response": "",
    }
    final_state = flow.invoke(initial_state)
    return {
        "insurance_summary" : final_state["is_insurance_summary"] ,
        "valid_summary" : final_state["is_valid"] ,
        "missing_fields" : final_state["missing_fields"] ,
        "suggestions" : final_state["suggestions"] ,
        "approved" : final_state["policy_approved"] ,
        "rejection_reason" : final_state["failed_criteria"] ,
        "message" : final_state["final_response"],
    }