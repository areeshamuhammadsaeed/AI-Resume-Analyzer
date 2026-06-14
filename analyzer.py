import os
import streamlit as st
import pdfplumber
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# =====================================================================
# 1. EMPOWER FRONTEND PAGE CONFIGURATION
# =====================================================================
st.set_page_config(page_title="AI Resume Intelligence Analyzer", page_icon="🤖", layout="wide")

st.title("🤖 AI Resume Intelligence Analyzer")
st.markdown("Upload any tech resume PDF and provide a target job role description to run an automated, data-driven evaluation.")
st.markdown("---")

# =====================================================================
# 2. DATA STRUCUTRE Blueprints
# =====================================================================
class GapsChecklist(BaseModel):
    missing_keywords: List[str] = Field(description="Keywords missing from the resume.")
    missing_sections: List[str] = Field(description="Standard structural resume blocks missing.")
    weak_action_verbs: List[str] = Field(description="Passive verbs that need stronger replacements.")

class ResumeReport(BaseModel):
    score: int = Field(description="An overall score from 0 to 100.")
    improvements: List[str] = Field(description="Actionable advice pointers.")
    gaps_checklist: GapsChecklist = Field(description="Organized checklist of gaps.")

# =====================================================================
# 3. CONVERT STREAMLIT BYTES STREAM INTO PLAIN TEXT
# =====================================================================
def extract_text_from_uploaded_pdf(uploaded_file) -> str:
    """Reads a Streamlit uploaded file buffer memory into raw text."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# =====================================================================
# 4. CONNECT TO GEMINI
# =====================================================================
def analyze_resume(resume_text: str, job_description: str) -> ResumeReport:
    # Initializes client, reading directly from $env:GEMINI_API_KEY
    client = genai.Client()
    
    prompt = f"""
    You are an elite automated ATS parsing engine and technical executive recruiter. 
    Critically analyze the following Resume Text against the Target Job Role Requirements.
    
    ---
    RESUME TEXT:
    {resume_text}
    
    ---
    TARGET JOB ROLE REQUIREMENTS:
    {job_description}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ResumeReport,
            temperature=0.15
        ),
    )
    return response.parsed

# =====================================================================
# 5. UI LAYOUT INPUT CONTROLS
# =====================================================================
left_column, right_column = st.columns([1, 1], gap="large")

with left_column:
    st.subheader("📋 Document Input Processing")
    
    # Drag and drop upload block
    uploaded_pdf = st.file_uploader("Upload your Resume (PDF format only)", type=["pdf"])
    
    # Input target career text criteria
    target_job_description = st.text_area(
        "Target Job Description / Desired Role Profile", 
        placeholder="Paste the target job description details here to cross-examine keywords...",
        height=200
    )
    
    # Submit activation trigger
    submit_button = st.button("Analyze Resume Data Matrix", type="primary", use_container_width=True)

# =====================================================================
# 6. PROCESSING AND OUTPUT DISPLAY METRICS
# =====================================================================
with right_column:
    st.subheader("📊 Intelligence Evaluation Matrix")
    
    if submit_button:
        if not uploaded_pdf:
            st.error("Please upload a resume file first.")
        elif not target_job_description.strip():
            st.error("Please provide a target job description to allow keyword auditing.")
        else:
            # Check for API Key presence before processing
            if "GEMINI_API_KEY" not in os.environ:
                st.error("API Authorization token missing! Please run `$env:GEMINI_API_KEY='your_key'` inside your terminal first.")
            else:
                with st.spinner("Decoding document layouts & computing matching metrics via Gemini AI..."):
                    try:
                        # 1. Parse PDF text
                        extracted_text = extract_text_from_uploaded_pdf(uploaded_pdf)
                        
                        # 2. Fetch AI object
                        report = analyze_resume(extracted_text, target_job_description)
                        
                        # 3. Display Score metric gauge colors conditionally
                        if report.score >= 80:
                            st.success(f"### Score: {report.score}/100 — Strong Match Profile!")
                        elif report.score >= 50:
                            st.warning(f"### Score: {report.score}/100 — Standard Baseline Profile (Requires Optimization)")
                        else:
                            st.error(f"### Score: {report.score}/100 — High Risk Profile (Heavy Remediation Needed)")
                        
                        # Tabs for cleanly sorting information
                        tab1, tab2, tab3 = st.tabs(["💡 Improvements Needed", "🔍 Keyword Gaps", "⚠️ Structural Items"])
                        
                        with tab1:
                            for item in report.improvements:
                                st.markdown(f"- {item}")
                                
                        with tab2:
                            st.markdown("#### Missing Target Keywords:")
                            for kw in report.gaps_checklist.missing_keywords:
                                st.checkbox(f"Missing Key Term: **{kw}**", value=False, disabled=True)
                                
                            st.markdown("#### Passive / Weak Action Words Found:")
                            for verb in report.gaps_checklist.weak_action_verbs:
                                st.markdown(f"❌ *Should replace usage of:* `{verb}`")
                                
                        with tab3:
                            st.markdown("#### Missing Structural Sections:")
                            if report.gaps_checklist.missing_sections:
                                for section in report.gaps_checklist.missing_sections:
                                    st.markdown(f"🚨 Missing Block: **{section}**")
                            else:
                                st.success("All structural essential layout components are present inside this document framework.")
                                
                    except Exception as error_msg:
                        st.error(f"An unexpected parsing execution failure occurred: {error_msg}")
    else:
        st.info("Awaiting file upload and operational activation matrix selection from left window panels.")