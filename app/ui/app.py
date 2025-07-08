import streamlit as st
import requests
import json
import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO


def process_markdown_line(line, styles):
    """Takes a markdown line and converts it to a PDF paragraph with proper styling"""
    line = line.strip()
    
    def convert_bold_text(text):
        """Handles bold text conversion from markdown to HTML for PDF rendering"""
        # Find and replace all **text** patterns with <b>text</b>
        return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    if line.startswith('## '):
        # Handle main section headers (## Header)
        heading_style = ParagraphStyle(
            'H2Style', parent=styles['Heading2'], fontSize=12, 
            spaceAfter=8, spaceBefore=12, textColor=colors.darkblue
        )
        text = convert_bold_text(line[3:])
        return Paragraph(text, heading_style)
    elif line.startswith('### '):
        # Handle subsection headers (### Subheader)
        heading_style = ParagraphStyle(
            'H3Style', parent=styles['Heading3'], fontSize=11, 
            spaceAfter=6, spaceBefore=10, textColor=colors.darkgreen
        )
        text = convert_bold_text(line[4:])
        return Paragraph(text, heading_style)
    elif line.startswith('* '):
        # Handle bullet points (* Item)
        bullet_style = ParagraphStyle(
            'BulletStyle', parent=styles['Normal'], fontSize=10, 
            leftIndent=20, spaceAfter=4
        )
        text = convert_bold_text(line[2:])
        return Paragraph(f"• {text}", bullet_style)
    elif line.startswith('        + ') or line.startswith('\t+ '):
        # Handle sub-bullet points (indented + subitem)
        sub_bullet_style = ParagraphStyle(
            'SubBulletStyle', parent=styles['Normal'], fontSize=10, 
            leftIndent=40, spaceAfter=4
        )
        text = convert_bold_text(line.split('+ ', 1)[1])
        return Paragraph(f"◦ {text}", sub_bullet_style)
    elif line:
        # Handle regular text lines
        text = convert_bold_text(line)
        return Paragraph(text, styles['Normal'])
    else:
        # Handle empty lines with spacing
        return Spacer(1, 6)
    

def create_pdf_report(report_data):
    """Builds a professional PDF report from the validation results and summary data"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add the main title at the top
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'], fontSize=16,
            spaceAfter=30, alignment=1, textColor=colors.darkblue
        )
        story.append(Paragraph("MediCheck Clinical Summary Report", title_style))
        story.append(Spacer(1, 20))
        
        # Include validation message if available
        if report_data.get("message"):
            story.append(Paragraph("Message:", styles['Heading2']))
            message_text = str(report_data["message"]).replace('\n', '<br/>')
            story.append(Paragraph(message_text, styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Add the patient summary with proper markdown formatting
        if report_data.get("summary"):
            story.append(Paragraph("Clinical Summary:", styles['Heading2']))
            
            # Convert markdown to PDF-friendly format
            lines = report_data["summary"].split('\n')
            for line in lines:
                element = process_markdown_line(line, styles)
                story.append(element)
            
            story.append(Spacer(1, 15))
        
        # Add timestamp for record keeping
        if report_data.get("generated_at"):
            story.append(Paragraph(f"Generated: {report_data['generated_at']}", styles['Italic']))
        
        # Safety check - always include some content
        if not story:
            story.append(Paragraph("No data available", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        # Create a simple error report if something goes wrong
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Error generating PDF report", styles['Heading1'])]
        doc.build(story)
        buffer.seek(0)
        return buffer


def main():
    st.set_page_config(page_title="MediCheck: AI Validator for Clinical Summaries", page_icon="🩺")
    st.title("🩺 MediCheck: AI Validator for Clinical Summaries")

    # Set up session variables to remember user's data between interactions
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
    if 'clean_report' not in st.session_state:
        st.session_state.clean_report = None
    if 'summary_generated' not in st.session_state:
        st.session_state.summary_generated = None
    if 'last_json_file' not in st.session_state:
        st.session_state.last_json_file = None
    if 'last_pdf_file' not in st.session_state:
        st.session_state.last_pdf_file = None



    # 📋 Instructions
    st.markdown("""
    ### 🧾 How to Use MediCheck
    
    **📂 Upload Options:**
    1. **JSON File**: Upload a structured clinical summary in JSON format
    2. **PDF File**: Upload a clinical summary document in PDF format
    
    **🔍 Validation Process:**
    1. **Guardrail Check**: AI determines if the document is a valid clinical summary for insurance
    2. **Field Validation**: AI checks for required fields and data quality
    3. **Policy Evaluation**: AI evaluates against insurance approval criteria
    
    **📋 Summary Generation:**
    - Generate patient summaries for any validation outcome (except guardrail failures)
    - Summaries include structured patient information with markdown formatting
    
    **📄 Download Options:**
    - **Initial Report**: Download validation results as PDF
    - **Updated Report**: Download validation results + patient summary as PDF
    - Reports include timestamps and professional formatting
    
    **🎯 Possible Outcomes:**
    - ✅ **Approved**: All checks passed
    - ⚠️ **Validation Warning**: Missing fields or quality issues
    - ❌ **Policy Rejected**: Valid summary but doesn't meet policy criteria
    - 📝 **Guardrail Failed**: Document not recognized as clinical summary
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

    # Reset results when user uploads different files
    current_json_file = uploaded_file.name if uploaded_file else None
    current_pdf_file = uploaded_pdf.name if uploaded_pdf else None
    
    if (current_json_file != st.session_state.last_json_file or 
        current_pdf_file != st.session_state.last_pdf_file):
        st.session_state.validation_result = None
        st.session_state.clean_report = None
        st.session_state.summary_generated = None
        st.session_state.last_json_file = current_json_file
        st.session_state.last_pdf_file = current_pdf_file

    # Handle JSON file uploads and validation
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
                    
                    # Prepare the report data for display and PDF generation
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
                    
                    # Save results for display and future use
                    st.session_state.validation_result = result
                    st.session_state.clean_report = clean_report
                    st.session_state.summary_generated = None
                    
                    # Refresh the page to show results
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Failed to parse JSON file: {e}")

    # Handle PDF file uploads, extraction, and validation
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
                message = result.get("message", "")
                
                # Set up report data based on extraction success
                if not result.get("insurance_summary", False):
                    # PDF wasn't a valid clinical summary or extraction failed
                    clean_report = {
                        "uploaded_data": {},
                        "message": message,
                        "generated_at": datetime.now().isoformat()
                    }
                else:
                    # Successfully extracted clinical data from PDF
                    extracted_json = result.get("input_json", {})
                    clean_report = {
                        "uploaded_data": extracted_json,
                        "message": message,
                        "generated_at": datetime.now().isoformat()
                    }
                
                # Save results for display and future use
                st.session_state.validation_result = result
                st.session_state.clean_report = clean_report
                st.session_state.summary_generated = None
                
                # Refresh the page to show results
                st.rerun()
            else:
                st.error(f"❌ Server error: Status code {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.text(response.text)

    # Show validation results when available
    if st.session_state.validation_result is not None:
        result = st.session_state.validation_result
        clean_report = st.session_state.clean_report
        message = result.get("message", "")
        
        # Generate PDF report for download
        try:
            pdf_buffer = create_pdf_report(clean_report)
            pdf_data = pdf_buffer.getvalue()
            
            # Provide download option for the report
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="download_initial_pdf"
            )
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            st.info("Please try again or contact support.")
        
        st.markdown("---")
        st.subheader("🧾 Validation Result")

        # Show different messages based on validation outcome
        if not result.get("insurance_summary", False):
            # Document wasn't recognized as a clinical summary
            st.info(f"📝 Guardrail Failed: {message}")
        
        elif result.get("insurance_summary", False) and not result.get("valid_summary", False):
            # Document is a clinical summary but has validation issues
            st.markdown(f'<div style="background-color:#fff3cd;padding:16px;border-radius:6px;color:#856404;border:1px solid #ffeeba;font-weight:bold;">⚠️ {message}</div>', unsafe_allow_html=True)
            if st.button("📝 Generate Summary", key="summary_validation_fail"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(f"{backend_url}/api/summary", json=st.session_state.clean_report["uploaded_data"])
                    if summary_response.status_code == 200:
                        summary_generated = summary_response.json().get("summary", "No summary returned.")
                        st.session_state.summary_generated = summary_generated
                        st.session_state.clean_report["summary"] = summary_generated
                        st.rerun()
                    else:
                        st.error("Failed to generate summary.")

        elif result.get("valid_summary", False) and not result.get("approved", False):
            # Summary is valid but doesn't meet insurance policy requirements
            st.error(f"❌ Policy Rejected: {message}")
            if st.button("📝 Generate Summary", key="summary_policy_fail"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(f"{backend_url}/api/summary", json=st.session_state.clean_report["uploaded_data"])
                    if summary_response.status_code == 200:
                        summary_generated = summary_response.json().get("summary", "No summary returned.")
                        st.session_state.summary_generated = summary_generated
                        st.session_state.clean_report["summary"] = summary_generated
                        st.rerun()
                    else:
                        st.error("Failed to generate summary.")

        elif result.get("approved", False):
            # All validation checks passed successfully
            st.success(f"✅ Approved: {message}")
            if st.button("📝 Generate Summary", key="summary_policy_pass"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(f"{backend_url}/api/summary", json=st.session_state.clean_report["uploaded_data"])
                    if summary_response.status_code == 200:
                        summary_generated = summary_response.json().get("summary", "No summary returned.")
                        st.session_state.summary_generated = summary_generated
                        st.session_state.clean_report["summary"] = summary_generated
                        st.rerun()
                    else:
                        st.error("Failed to generate summary.")

        else:
            # Something unexpected happened
            st.warning("⚠️ Unexpected response. Please check backend output.")
        
        # Show the generated patient summary when available
        if st.session_state.summary_generated:
            st.markdown("### 📋 Patient Summary")
            st.write(st.session_state.summary_generated)
            
            # Create updated PDF with summary included
            try:
                updated_pdf_buffer = create_pdf_report(st.session_state.clean_report)
                updated_pdf_data = updated_pdf_buffer.getvalue()
                
                st.download_button(
                    label="📄 Download Updated PDF Report",
                    data=updated_pdf_data,
                    file_name=f"validation_report_with_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_updated_pdf"
                )
            except Exception as e:
                st.error(f"Error creating updated PDF: {str(e)}")
                st.info("Please try again or contact support.")


if __name__ == "__main__":
    main()