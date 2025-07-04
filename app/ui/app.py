import streamlit as st
import requests
import json
import os
from collections import defaultdict

def main():
    st.set_page_config(page_title="MediCheck: AI Validator for Clinical Summaries", page_icon="🩺")
    st.title("🩺 MediCheck: AI Validator for Clinical Summaries")

    st.write("""
    Upload a clinical summary JSON file to validate it for insurance approval.
    The app will show clear results for Guardrails, Validation, or Policy checks.
    """)

    # Get backend URL from environment or use default
    backend_url = os.getenv("BACKEND_URL", "https://medicheck-fgpn.onrender.com")
    
    uploaded_file = st.file_uploader("Choose a clinical summary JSON file", type=["json"])

    if uploaded_file is not None:
        try:
            json_data = json.load(uploaded_file)
            st.subheader("Uploaded JSON:")
            st.json(json_data, expanded=False)

            if st.button("Validate Summary"):
                with st.spinner("Validating..."):
                    response = requests.post(
                        f"{backend_url}/api/validate-summary",
                        json=json_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        message = result.get("message", "")
                        # CASE 1 — Not intended for insurance approval (Guardrail fail)
                        if not result.get("insurance_summary", False):
                            st.info(f"📝✏️ {message}")
                            if st.button("Revise Note"):
                                st.experimental_rerun()
                        # CASE 2 — Missing required information (Validation fail)
                        elif result.get("insurance_summary", False) and not result.get("valid_summary", False):
                            st.warning(f"⚠️🗂️ {message}", icon="⚠️")
                        # CASE 3 — Application denied (Policy fail)
                        elif (
                            result.get("insurance_summary", False)
                            and result.get("valid_summary", False)
                            and not result.get("approved", False)
                        ):
                            st.error(f"❌🔒 {message}")
                            if st.button("Contact Support"):
                                st.write("Support contact feature coming soon!")
                        # CASE 4 — Application approved (Success)
                        elif (
                            result.get("insurance_summary", False)
                            and result.get("valid_summary", False)
                            and result.get("approved", False)
                        ):
                            st.success(f"🎉✅ {message}")
                            st.balloons()
                            if st.button("View Policy Details"):
                                st.write("Policy details feature coming soon!")
                        else:
                            st.warning("⚠️ Unexpected response. Please check the backend or your input.")

        except Exception as e:
            st.error(f"Invalid JSON file: {e}")

if __name__ == "__main__":
    main()
    