import streamlit as st
import requests
import json
import os
from datetime import datetime


def main():
    st.set_page_config(page_title="MediCheck: AI Validator for Clinical Summaries", page_icon="🩺")
    st.title("🩺 MediCheck: AI Validator for Clinical Summaries")

    # 📋 Instructions
    st.markdown("""
    ### 🧾 How to Use MediCheck
    1. **Upload** a clinical summary JSON file (format shown below).
    2. **Click "Validate Summary"** to let our AI evaluate it.
    3. **Review the validation results**, including any missing fields.
    """)

    st.markdown("---")

    # Sample JSON button
    sample_json = {
        "patient_demographics": {
            "full_name": "Alice Green",
            "age": 65,
            "gender": "Female",
            "weight": 68.0,
            "insurance_id": "INS-345678",
            "alcohol_use": False,
            "smoking": False,
            "substance_addiction": False
        },
        "hpi": {
            "chief_complaint": "Shortness of breath",
            "duration": "1 week",
            "onset": "Sudden",
            "associated_symptoms": ["Cough", "Fever"],
            "documentation_date": "2024-06-01",
            "vitals": {
                "blood_pressure": "118/76",
                "heart_rate": 78,
                "temperature": 37.0
            }
        },
        "past_medical_history": {
            "chronic_illnesses": ["Hypertension"],
            "surgical_history": ["Cholecystectomy"],
            "allergies": ["None"],
            "medication_history": ["Amlodipine"]
        },
        "procedures_treatments": [
            {
                "date": "2024-06-01",
                "procedure_name": "Bronchoscopy",
                "performing_physician": "Dr. Patel",
                "justification": "Evaluate persistent cough",
                "referral_note_attached": True
            }
        ],
        "imaging_lab_results": [
            {
                "type": "CT Chest",
                "date": "2024-06-01",
                "findings": "Patchy infiltrates"
            },
            {
                "type": "CBC",
                "date": "2024-06-01",
                "findings": "Elevated WBC"
            }
        ],
        "diagnosis_discharge_summary": {
            "final_diagnosis": "Pneumonia",
            "icd_10_code": "J18.9",
            "treatment_summary": "Antibiotics, supportive care",
            "discharge_plan": "Follow-up in 2 weeks"
        },
        "physician_signature": {
            "attending_physician": "Dr. Patel",
            "date_of_report": "2024-06-02",
            "digital_signature": "PATEL2024SIG"
        }
    }

    st.download_button("📥 Download Sample JSON", data=json.dumps(sample_json, indent=2),
                       file_name="sample_clinical_summary.json", mime="application/json")

    st.markdown("---")

    # File upload
    uploaded_file = st.file_uploader("📂 Upload Clinical Summary JSON", type=["json"])
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").strip()

    if uploaded_file:
        st.success(f"✅ Uploaded: `{uploaded_file.name}` ({uploaded_file.size / 1024:.2f} KB)")
        try:
            json_data = json.load(uploaded_file)
            st.markdown("### 🔍 Preview of Uploaded Data")
            st.json(json_data, expanded=False)

            if st.button("🧠 Validate Summary"):
                with st.spinner("Validating clinical summary..."):
                    response = requests.post(
                        f"{backend_url}/api/validate-summary",
                        json=json_data
                    )

                if response.status_code == 200:
                    result = response.json()
                    message = result.get("message", "")
                    combined_report = {
                        "submitted_summary": json_data,
                        "validation_result": result,
                        "validated_at": datetime.now().isoformat()
                    }

                    report_str = json.dumps(combined_report, indent=2)
                    st.download_button(
                        label="📄 Download Validation Report",
                        data=report_str,
                        file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    st.markdown("---")
                    st.subheader("🧾 Validation Result")

                    # CASE 1 — Guardrail fail
                    if not result.get("insurance_summary", False):
                        st.info(f"📝 Guardrail Failed: {message}")
                    
                    # CASE 2 — Validation fail
                    elif result.get("insurance_summary", False) and not result.get("valid_summary", False):
                        st.warning(f"⚠️ Validation Warning: {message}")
                        missing_fields = result.get("missing_fields", {})
                        if missing_fields:
                            st.markdown("#### ❗ Missing Sections:")
                            for section, fields in missing_fields.items():
                                st.markdown(f"- **{section.title()}**: {', '.join(fields)}")

                    # CASE 3 — Policy check failed
                    elif result.get("valid_summary", False) and not result.get("approved", False):
                        st.error(f"❌ Policy Rejected: {message}")

                    # CASE 4 — All checks passed
                    elif result.get("approved", False):
                        st.success(f"✅ Approved: {message}")

                    else:
                        st.warning("⚠️ Unexpected response. Please check backend output.")
                else:
                    st.error(f"❌ Server error: Status code {response.status_code}")
                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)

        except Exception as e:
            st.error(f"❌ Failed to parse JSON file: {e}")
        
if __name__ == "__main__":
    main()


