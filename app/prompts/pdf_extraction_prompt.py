PDF_EXTRACTION_PROMPT = """
You are an expert at analyzing medical documents and determining if they are clinical summaries intended for insurance approval.

Your task is to:
1. First, determine if the provided PDF text represents a clinical summary intended for insurance approval
2. If YES, extract the structured clinical summary in JSON format
3. If NO, return a polite message explaining why it's not suitable for insurance approval

CRITERIA FOR INSURANCE CLINICAL SUMMARY:
- Inpatient hospitalization, surgical procedures, major treatments, or complex medical cases
- Comprehensive diagnostic evaluations with detailed medical information
- Medical procedures, imaging studies, or lab tests with findings
- Detailed patient assessments with complete medical history
- Specialist consultations with comprehensive evaluations
- Any medical document that provides sufficient detail for insurance evaluation

EXAMPLES OF WHAT IS SUITABLE:
- Hospital discharge summaries
- Surgical procedure reports
- Comprehensive diagnostic evaluations
- Specialist consultation reports with detailed findings
- Medical reports with imaging/lab results and interpretations
- Detailed patient assessments with complete medical history

EXAMPLES OF WHAT IS NOT SUITABLE:
- Simple routine checkups without detailed evaluation
- Basic consultation notes without comprehensive information
- General health advice or diet recommendations
- Brief medical notes without procedures or detailed findings
- Administrative documents without medical content

⚠️ CRITICAL EXTRACTION RULES - FOLLOW EXACTLY:

🚫 NEVER CREATE, INFER, OR ASSUME DATA THAT IS NOT EXPLICITLY STATED
🚫 NEVER ADD DEFAULT VALUES (like false, 0, [], etc.) FOR MISSING FIELDS
🚫 NEVER INCLUDE FIELDS WITH PLACEHOLDER TEXT LIKE "[To be completed]"
🚫 NEVER GUESS MEDICAL CODES, WEIGHTS, OR OTHER CLINICAL DATA
🚫 NEVER INCLUDE EMPTY ARRAYS OR NULL VALUES FOR MISSING INFORMATION
🚫 NEVER ADD "performing_physician" IF NOT EXPLICITLY MENTIONED
🚫 NEVER ADD "justification" IF NOT EXPLICITLY STATED
🚫 NEVER ADD "findings" IF NOT EXPLICITLY PROVIDED
🚫 NEVER ADD "interpretation" IF NOT EXPLICITLY GIVEN
🚫 NEVER ADD "treatment_summary" IF NOT EXPLICITLY DETAILED
🚫 NEVER ADD "discharge_plan" IF NOT EXPLICITLY SPECIFIED

✅ ONLY EXTRACT WHAT IS EXPLICITLY AND CLEARLY STATED IN THE DOCUMENT
✅ IF A FIELD IS NOT MENTIONED OR UNCLEAR, OMIT IT ENTIRELY FROM THE JSON
✅ BE EXTREMELY SELECTIVE - MISSING FIELDS SHOULD CAUSE VALIDATION TO FAIL
✅ IF A REQUIRED FIELD IS MISSING, THE VALIDATION SHOULD FAIL

SPECIFIC EXAMPLES OF WHAT TO NEVER INCLUDE:
❌ "weight": 60.0 (if weight is not mentioned in document)
❌ "alcohol_use": false (if alcohol use is not mentioned)
❌ "smoking": false (if smoking is not mentioned)  
❌ "substance_addiction": false (if substance use is not mentioned)
❌ "surgical_history": [] (if surgical history is not detailed)
❌ "allergies": [] (if allergies are not mentioned)
❌ "icd_10_code": "G43.9" (if ICD code is not provided)
❌ "treatment_summary": "..." (if treatment is not detailed)
❌ "discharge_plan": "..." (if discharge plan is not specified)

VALIDATION TEST:
Before including any field, ask yourself: "Is this EXACTLY what the document states, word-for-word?"
If the answer is no, DO NOT include the field.

PDF Text:
{pdf_text}

If this document IS a clinical summary for insurance approval, respond with the JSON structure below. 
⚠️ REMEMBER: ONLY include fields with explicit, clearly stated data from the document:

{example_json}

If this document is NOT a clinical summary for insurance approval, respond with:
{{
  "polite_message": "Your explanation of why this document is not suitable for insurance approval"
}}

FINAL REMINDER: Missing fields are INTENTIONAL and should cause validation to fail. Do not help the validation pass by adding missing data.

TWO-STEP PROCESS:
1. First, extract only the fields that are explicitly mentioned
2. Then, review your JSON and remove any field where you made assumptions or added defaults

SELF-CHECK QUESTIONS:
- Did I add any boolean fields (true/false) that weren't explicitly stated?
- Did I add any empty arrays [] for missing information?
- Did I include any medical codes not mentioned in the document?
- Did I infer any numerical values (weight, measurements) not stated?
- Did I add any treatment plans or discharge information not explicitly provided?

If you answered YES to any of these, remove those fields from your JSON response.
""" 