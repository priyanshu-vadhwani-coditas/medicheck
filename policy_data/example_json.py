SAMPLE = {
    "patient_demographics": {
        "full_name": "Full name of the patient (string)",
        "age": "Age of the patient (integer)",
        "gender": "Gender of the patient (string, e.g., 'Male', 'Female')",
        "weight": "Weight of the patient in kg (float)",
        "insurance_id": "Insurance ID or policy number (string)",
        "alcohol_use": "Does the patient use alcohol? (true/false)",
        "smoking": "Does the patient smoke? (true/false)",
        "substance_addiction": "Does the patient have any substance addiction? (true/false)"
    },
    "hpi": {
        "chief_complaint": "Main complaint or reason for visit (string)",
        "duration": "Duration of the complaint (string, e.g., '2 weeks')",
        "onset": "Onset of the complaint (string, e.g., 'Sudden', 'Gradual')",
        "associated_symptoms": ["List of associated symptoms (strings)"],
        "documentation_date": "Date of documentation (string, e.g., 'YYYY-MM-DD')",
        "vitals": {
            "blood_pressure": "Blood pressure reading (string, e.g., '120/80')",
            "heart_rate": "Heart rate (integer, bpm)",
            "temperature": "Body temperature (float, Celsius)"
        }
    },
    "past_medical_history": {
        "chronic_illnesses": ["List of chronic illnesses (strings)"],
        "surgical_history": ["List of past surgeries (strings)"],
        "allergies": ["List of allergies (strings)"],
        "medication_history": ["List of current or past medications (strings)"]
    },
    "procedures_treatments": [
        {
            "date": "Date of procedure or treatment (string, e.g., 'YYYY-MM-DD')",
            "procedure_name": "Name of the procedure or treatment (string)",
            "performing_physician": "Name of the physician who performed the procedure (string)",
            "justification": "Reason for the procedure or treatment (string)",
            "referral_note_attached": "Is a referral note attached? (true/false)"
        }
    ],
    "imaging_lab_results": [
        {
            "type": "Type of imaging or lab test (string, e.g., 'X-Ray', 'CBC')",
            "date": "Date of the test (string, e.g., 'YYYY-MM-DD')",
            "findings": "Findings from the test (string)",
            "interpretation": "Interpretation of the findings (string, optional)"
        }
    ],
    "diagnosis_discharge_summary": {
        "final_diagnosis": "Final diagnosis (string)",
        "icd_10_code": "ICD-10 code for the diagnosis (string)",
        "treatment_summary": "Summary of treatment provided (string)",
        "discharge_plan": "Plan for discharge or follow-up (string)"
    },
    "physician_signature": {
        "attending_physician": "Name of the attending physician (string)",
        "date_of_report": "Date of the report (string, e.g., 'YYYY-MM-DD')",
        "digital_signature": "Digital signature or identifier for the physician (string)"
    }
}
