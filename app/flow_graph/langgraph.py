import os
import time
import asyncio
from typing import Dict, Any, TypedDict, List
from typing_extensions import TypedDict
import json
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from app.services.guardrail import check_is_insurance_summary
from app.services.validator import validate_clinical_summary
from app.services.policy import evaluate_policy
from app.services.pdf_validator import extract_clinical_summary_from_pdf
from app.services.summary import summary_generator

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
    summary: str

async def guardrail_node(state: AgentState) -> AgentState:
    """
    Node: Checks if the input JSON or pdf is a valid insurance summary using the LLM guardrail.
    Now async to handle async service calls.
    """
    start_time = time.time()
    print(f"DEBUG: GUARDRAIL NODE START - {start_time}")
    
    result = await check_is_insurance_summary(state["input_json"])
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: GUARDRAIL NODE END - Duration: {duration:.2f} seconds")
    
    state["is_insurance_summary"] = result.get("is_insurance_summary", False)
    if state["is_insurance_summary"] == False:
        state["final_response"] = result.get("polite_message")
    return state

async def validation_node(state: AgentState) -> AgentState:
    """
    Node: Validates the clinical summary fields and provides LLM-generated suggestions if invalid.
    Now async to handle async service calls.
    """
    start_time = time.time()
    print(f"DEBUG: VALIDATION NODE START - {start_time}")
    
    result = await validate_clinical_summary(state["input_json"])
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: VALIDATION NODE END - Duration: {duration:.2f} seconds")
    
    state["is_valid"] = result["is_valid"]
    state["missing_fields"] = result["missing_fields"]
    state["suggestions"] = result["suggestions"]
    
    if not state["is_valid"]:
        validation_message = "Clinical summary validation failed:\n\n"
        
        if result.get("missing_fields"):
            validation_message += "**Missing Required Fields:**\n"
            for field in result["missing_fields"]:
                validation_message += f"• {field}\n"
            validation_message += "\n"
        
        if result.get("suggestions"):
            validation_message += "**Suggestions:**\n"
            for suggestion in result["suggestions"]:
                validation_message += f"• {suggestion}\n"
        
        state["final_response"] = validation_message
        else:
        state["final_response"] = "Clinical summary validation passed successfully."
    
    return state

async def policy_node(state: AgentState) -> AgentState:
    """
    Node: Evaluates the clinical summary against the insurance policy using the LLM.
    Now async to handle async service calls.
    """
    start_time = time.time()
    print(f"DEBUG: POLICY NODE START - {start_time}")
    
    result = await evaluate_policy(state["input_json"])
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: POLICY NODE END - Duration: {duration:.2f} seconds")
    
    state["policy_approved"] = result["policy_approved"]
    state["failed_criteria"] = result["failed_criteria"]
    state["final_response"] = result["policy_message"]
    return state

async def pdf_extraction_node(state: AgentState) -> AgentState:
    """
    Node: Extracts clinical summary from PDF and handles extraction failures.
    Now async to handle the async PDF extraction function.
    """
    start_time = time.time()
    print(f"DEBUG: PDF EXTRACTION NODE START - {start_time}")
    
    result = await extract_clinical_summary_from_pdf(state["pdf_path"])
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: PDF EXTRACTION NODE END - Duration: {duration:.2f} seconds")
    
    if "polite_message" not in result:
        state["input_json"] = result
        state["final_response"] = "PDF extraction successful."
    else:
        state["final_response"] = result.get("polite_message", "Unknown PDF extraction error.")
        state["is_insurance_summary"] = False 
    return state

async def summary_node(state: AgentState) -> AgentState:
    """
    Node: Generates a summary when explicitly requested.
    Now async to handle async service calls.
    """
    start_time = time.time()
    print(f"DEBUG: SUMMARY NODE START - {start_time}")
    
    state["summary"] = await summary_generator(state["input_json"])
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: SUMMARY NODE END - Duration: {duration:.2f} seconds")
    
    return state

async def input_router(state: AgentState) -> str:
    """
    Router: Decides whether to process JSON or PDF input.
    Now async for consistency with other async functions.
    """
    if state.get("pdf_path"):
        return "pdf_extraction"
    else:
        return "guardrail"

async def guardrail_router(state: AgentState) -> str:
    """
    Router: Decides whether to proceed to validation or end if not an insurance summary.
    Now async for consistency with other async functions.
    """
    if state["is_insurance_summary"] == False:
        return END
    else:
        return "validation"

async def validation_router(state: AgentState) -> str:
    """
    Router: Decides whether to proceed to policy evaluation or end if validation fails.
    Now async for consistency with other async functions.
    """
    
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

def create_summary_flow() -> StateGraph:
    """
    Constructs a flow graph specifically for summary generation.
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("summary", summary_node)
    workflow.add_edge(START, "summary")
    workflow.add_edge("summary", END)
    return workflow.compile()

async def process_clinical_summary(input_json: Dict[str, Any] = None, pdf_path: str = None) -> Dict[str, Any]:
    """
    Orchestrates the validation flow for a clinical summary JSON or PDF.
    Returns the full final state with all details for frontend handling.
    Now async to handle async PDF extraction.
    """
    total_start_time = time.time()
    print(f"DEBUG: TOTAL FLOW START - {total_start_time}")
    
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
        "summary": "",
    }
    final_state = await flow.ainvoke(initial_state)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    print(f"DEBUG: TOTAL FLOW END - Duration: {total_duration:.2f} seconds")
    
    return {
        "input_json": final_state["input_json"],
        "insurance_summary" : final_state["is_insurance_summary"] ,
        "valid_summary" : final_state["is_valid"] ,
        "missing_fields" : final_state["missing_fields"] ,
        "suggestions" : final_state["suggestions"] ,
        "approved" : final_state["policy_approved"] ,
        "rejection_reason" : final_state["failed_criteria"] ,
        "message" : final_state["final_response"],
    }

async def process_summary_generation(input_json: Dict[str, Any]) -> str:
    """
    Generates a summary for the given clinical summary JSON.
    Returns the summary as a string.
    Now async to handle async summary generation.
    """
    start_time = time.time()
    print(f"DEBUG: SUMMARY GENERATION START - {start_time}")
    
    flow = create_summary_flow()
    initial_state: AgentState = {
        "input_json": input_json,
        "pdf_path": "",
        "is_insurance_summary": False,
        "is_valid": False,
        "missing_fields": [],
        "suggestions": [],
        "policy_approved": False,
        "failed_criteria": [],
        "final_response": "",
        "summary": "",
    }
    final_state = await flow.ainvoke(initial_state)
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"DEBUG: SUMMARY GENERATION END - Duration: {duration:.2f} seconds")
    
    return final_state["summary"]