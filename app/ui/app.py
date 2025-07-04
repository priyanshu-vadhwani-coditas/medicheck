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

                        # ✅ CASE 1 — Rejected by Guardrails
                        if not result.get("insurance_summary", False):
                            st.error(f"❌ {result.get('message', 'Rejected by guardrails.')}")
                        
                        # ✅ CASE 2 — Rejected by Validation
                        elif result.get("insurance_summary", False) and not result.get("valid_summary", False):
                            st.error(f"❌ {result.get('message', 'Validation failed.')}")
                            missing_fields = result.get("missing_fields", [])
                            if missing_fields:
                                st.write("**Missing Fields:**")
                                def group_missing_fields(missing_fields):
                                    grouped = defaultdict(list)
                                    for field in missing_fields:
                                        parts = field.split('.')
                                        if len(parts) > 1:
                                            grouped[parts[0]].append(".".join(parts[1:]))
                                        else:
                                            grouped[parts[0]].append(None)
                                    return grouped
                                grouped = group_missing_fields(missing_fields)
                                for section, fields in grouped.items():
                                    st.markdown(f"**{section}**")
                                    for field in fields:
                                        if field:
                                            st.markdown(f"&nbsp;&nbsp;&nbsp;<span style='color:red'>• {field}</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"&nbsp;&nbsp;&nbsp;<span style='color:red'>• (entire section missing)</span>", unsafe_allow_html=True)
                        
                        # ✅ CASE 3 — Rejected by Policy
                        elif (
                            result.get("insurance_summary", False)
                            and result.get("valid_summary", False)
                            and not result.get("approved", False)
                        ):
                            st.error(f"❌ {result.get('message', 'Policy rejection.')}")
                            rejection_reasons = result.get("rejection_reason", [])
                            if rejection_reasons:
                                st.write("**Rejection Reasons:**")
                                for reason in rejection_reasons:
                                    st.markdown(f"<span style='color:red'>• {reason}</span>", unsafe_allow_html=True)
                        
                        # ✅ CASE 4 — Approved
                        elif (
                            result.get("insurance_summary", False)
                            and result.get("valid_summary", False)
                            and result.get("approved", False)
                        ):
                            st.success(f"✅ {result.get('message', 'Approved.')}")
                        
                        else:
                            st.warning("⚠️ Unexpected response. Please check the backend or your input.")
                        
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"Invalid JSON file: {e}")

if __name__ == "__main__":
    main()
    