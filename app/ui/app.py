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
    1. **Upload** a clinical summary JSON file **or** a PDF (see options below).
    2. **Click the appropriate button** to let our AI evaluate or extract and validate your summary.
    3. **Review the validation results**, including any missing fields or extraction details.
    """)

    st.markdown("---")

    # Side-by-side uploaders
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📂 Upload Clinical Summary JSON")
        uploaded_file = st.file_uploader("Upload JSON", type=["json"], key="json_uploader")
    with col2:
        st.markdown("#### 📄 Upload Clinical Summary PDF")
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")

    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").strip()

    # JSON flow
    if uploaded_file:
        st.success(f"✅ Uploaded: `{uploaded_file.name}` ({uploaded_file.size / 1024:.2f} KB)")
        try:
            json_data = json.load(uploaded_file)
            st.markdown("### 🔍 Preview of Uploaded Data")
            st.json(json_data, expanded=False)

            if st.button("🧠 Validate Summary", key="validate_json"):
                with st.spinner("Validating clinical summary..."):
                    response = requests.post(
                        f"{backend_url}/api/validate-summary",
                        json=json_data
                    )

                if response.status_code == 200:
                    result = response.json()
                    message = result.get("message", "")
                    summary_generated = ""
                    
                    # Create clean report structure
                    clean_report = {
                        "uploaded_data": json_data,
                        "message": message,
                        "validation_details": {
                            "insurance_summary": result.get("insurance_summary", False),
                            "valid_summary": result.get("valid_summary", False),
                            "approved": result.get("approved", False),
                            "missing_fields": result.get("missing_fields", []),
                            "rejection_reason": result.get("rejection_reason", [])
                        },
                        "generated_at": datetime.now().isoformat()
                    }

                    report_str = json.dumps(clean_report, indent=2)
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
                        if st.button("📝 Generate Summary", key="summary_validation_fail"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=json_data)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"validation_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

                    # CASE 3 — Policy check failed
                    elif result.get("valid_summary", False) and not result.get("approved", False):
                        st.error(f"❌ Policy Rejected: {message}")
                        if st.button("📝 Generate Summary", key="summary_policy_fail"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=json_data)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"validation_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

                    # CASE 4 — All checks passed
                    elif result.get("approved", False):
                        st.success(f"✅ Approved: {message}")
                        if st.button("📝 Generate Summary", key="summary_policy_pass"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=json_data)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"validation_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

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

    # PDF flow
    if uploaded_pdf:
        st.success(f"✅ Uploaded: `{uploaded_pdf.name}` ({uploaded_pdf.size / 1024:.2f} KB)")
        if st.button("Extract & Validate PDF", key="validate_pdf"):
            with st.spinner("Extracting and validating clinical summary from PDF..."):
                files = {"file": (uploaded_pdf.name, uploaded_pdf, "application/pdf")}
                response = requests.post(
                    f"{backend_url}/api/upload-pdf",
                    files=files
                )
            if response.status_code == 200:
                result = response.json()
                st.markdown("---")
                st.subheader("🧾 PDF Extraction & Validation Result")
                
                if "polite_message" in result:
                    st.info(result["polite_message"])
                else:
                    # Show extracted JSON data
                    if "input_json" in result:
                        st.markdown("### 🔍 Extracted Data")
                        st.json(result["input_json"], expanded=False)
                    
                    # Show validation results similar to JSON flow
                    message = result.get("message", "")
                    extracted_json = result.get("input_json", {})
                    
                    # Create clean report structure
                    clean_report = {
                        "uploaded_data": extracted_json,
                        "message": message,
                        "validation_details": {
                            "insurance_summary": result.get("insurance_summary", False),
                            "valid_summary": result.get("valid_summary", False),
                            "approved": result.get("approved", False),
                            "missing_fields": result.get("missing_fields", []),
                            "rejection_reason": result.get("rejection_reason", [])
                        },
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    # Download report
                    report_str = json.dumps(clean_report, indent=2)
                    st.download_button(
                        label="📄 Download PDF Extraction Report",
                        data=report_str,
                        file_name=f"pdf_extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    
                    # CASE 1 — Guardrail fail
                    if not result.get("insurance_summary", False):
                        st.info(f"📝 Guardrail Failed: {message}")
                    
                    # CASE 2 — Validation fail
                    elif result.get("insurance_summary", False) and not result.get("valid_summary", False):
                        st.warning(f"⚠️ Validation Warning: {message}")
                        missing_fields = result.get("missing_fields", {})
                        if st.button("📝 Generate Summary", key="summary_validation_fail_pdf"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=extracted_json)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"pdf_extraction_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

                    # CASE 3 — Policy check failed
                    elif result.get("valid_summary", False) and not result.get("approved", False):
                        st.error(f"❌ Policy Rejected: {message}")
                        if st.button("📝 Generate Summary", key="summary_policy_fail_pdf"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=extracted_json)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"pdf_extraction_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

                    # CASE 4 — All checks passed
                    elif result.get("approved", False):
                        st.success(f"✅ Approved: {message}")
                        if st.button("📝 Generate Summary", key="summary_policy_pass_pdf"):
                            with st.spinner("Generating summary..."):
                                summary_response = requests.post(f"{backend_url}/api/summary", json=extracted_json)
                                if summary_response.status_code == 200:
                                    summary_generated = summary_response.json().get("summary", "No summary returned.")
                                    st.markdown("### 📋 Patient Summary")
                                    st.write(summary_generated)
                                    # Update report with summary
                                    clean_report["summary"] = summary_generated
                                    report_str = json.dumps(clean_report, indent=2)
                                    st.download_button(
                                        label="📄 Download Updated Report",
                                        data=report_str,
                                        file_name=f"pdf_extraction_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                else:
                                    st.error("Failed to generate summary.")

                    else:
                        st.warning("⚠️ Unexpected response. Please check backend output.")
            else:
                st.error(f"❌ Server error: Status code {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.text(response.text)

if __name__ == "__main__":
    main()


