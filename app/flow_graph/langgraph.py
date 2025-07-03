import os
from typing import Dict, Any, TypedDict, List
from typing_extensions import TypedDict
import json
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from app.services.guardrail import check_is_insurance_summary
from app.services.validator import validate_clinical_summary
from app.services.policy import evaluate_policy

load_dotenv()


class AgentState(TypedDict):
    input_json: Dict[str, Any]
    is_insurance_summary: bool
    is_valid: bool
    missing_fields: List[str]
    suggestions: List[str]
    policy_approved: bool
    failed_criteria: List[str]
    policy_message: str
    final_response: str

def guardrail_node(state: AgentState) -> AgentState:
    print("[DEBUG] Entering guardrail_node with state:", state)
    result = check_is_insurance_summary(state["input_json"])
    state["is_insurance_summary"] = result.get("is_insurance_summary", False)
    if state["is_insurance_summary"] == False:
        state["final_response"] = result.get("polite_message")
    print("[DEBUG] Exiting guardrail_node with state:", state)
    return state

def validation_node(state: AgentState) -> AgentState:
    print("[DEBUG] Entering validation_node with state:", state)
    result = validate_clinical_summary(state["input_json"])
    state["is_valid"] = result["is_valid"]
    state["missing_fields"] = result["missing_fields"]
    state["suggestions"] = result["suggestions"]
    if not state["is_valid"]:
        state["final_response"] = (
            "Clinical summary is missing required fields: "
            + ", ".join(state["missing_fields"]) + ". Suggestions: "
            + "; ".join(state["suggestions"])
        )
    print("[DEBUG] Exiting validation_node with state:", state)
    return state

def policy_node(state: AgentState) -> AgentState:
    print("[DEBUG] Entering policy_node with state:", state)
    result = evaluate_policy(state["input_json"])
    state["policy_approved"] = result["policy_approved"]
    state["failed_criteria"] = result["failed_criteria"]
    state["policy_message"] = result["policy_message"]
    state["final_response"] = state["policy_message"]
    print("[DEBUG] Exiting policy_node with state:", state)
    return state

def guardrail_router(state: AgentState) -> str:
    if state["is_insurance_summary"] == False:
        return END
    else:
        return "validation"

def validation_router(state: AgentState) -> str:
    if state["is_valid"] == True:
        return "policy"
    else:
        return END

def create_validation_flow() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("policy", policy_node)

    workflow.add_edge(START, "guardrail")
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

def process_clinical_summary(input_json: Dict[str, Any]) -> Dict[str, Any]:
    print("[DEBUG] Starting process_clinical_summary with input_json:", input_json)
    flow = create_validation_flow()
    initial_state: AgentState = {
        "input_json": input_json,
        "is_insurance_summary": False,
        "is_valid": False,
        "missing_fields": [],
        "suggestions": [],
        "policy_approved": False,
        "failed_criteria": [],
        "policy_message": "",
        "final_response": "",
    }
    final_state = flow.invoke(initial_state)
    print("[DEBUG] Final state after flow:", final_state)
    return {
        "message": final_state["final_response"]
    }