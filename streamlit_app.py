import streamlit as st
import pdfplumber
import re
import json
import requests

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer (Grok)",
    page_icon="🎯",
    layout="wide",
)

# ─────────────────────────────
# SESSION STATE
# ─────────────────────────────
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "tool" not in st.session_state:
    st.session_state.tool = "📊 Deep Analysis"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ─────────────────────────────
# GROK API (SAFE VERSION)
# ─────────────────────────────
def call_grok(prompt):
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['GROK_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "grok-2-latest",
                "messages": [
                    {"role": "system", "content": "You are a career coach AI."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
            timeout=30,
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"API Error: {str(e)}"


# ─────────────────────────────
# PDF TEXT
# ─────────────────────────────
def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


# ─────────────────────────────
# SAFE ANALYSIS
# ─────────────────────────────
def analyze_resume(resume, job):
    if not resume or not job:
        return {"ats_score": 0, "summary": "Missing input"}

    prompt = f"""
Return ONLY valid JSON:
{{
"ats_score": number,
"summary": string,
"strengths": [],
"weaknesses": []
}}

RESUME:
{resume}

JOB:
{job}
"""

    raw = call_grok(prompt)

    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except:
        return {
            "ats_score": 0,
            "summary": "Failed to parse AI response",
            "strengths": [],
            "weaknesses": [],
        }


# ─────────────────────────────
# UI
# ─────────────────────────────
st.title("🎯 AI Resume Analyzer (Grok)")

# Sidebar
with st.sidebar:
    st.header("Upload Resume")

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        st.session_state.resume_text = extract_pdf(file)
        st.success("Resume loaded")

    st.session_state.tool = st.radio(
        "Select Tool",
        ["📊 Deep Analysis", "💬 Chat", "📝 Cover Letter", "🎤 Interview Prep"]
    )


# Job input
job = st.text_area("Paste Job Description", height=180)
st.session_state.job_description = job

st.markdown("---")


# ─────────────────────────────
# DEEP ANALYSIS
# ─────────────────────────────
if st.session_state.tool == "📊 Deep Analysis":

    if st.button("Analyze Resume"):

        if st.session_state.resume_text and st.session_state.job_description:
            st.session_state.analysis_result = analyze_resume(
                st.session_state.resume_text,
                st.session_state.job_description
            )
        else:
            st.warning("Upload resume and job description first")

    r = st.session_state.analysis_result

    if r:
        st.metric("ATS Score", r.get("ats_score", 0))
        st.write(r.get("summary", ""))
        st.write("Strengths:", r.get("strengths", []))
        st.write("Weaknesses:", r.get("weaknesses", []))


# ─────────────────────────────
# CHAT
# ─────────────────────────────
elif st.session_state.tool == "💬 Chat":

    q = st.text_input("Ask anything")

    if q and st.session_state.resume_text:
        prompt = f"""
Resume:
{st.session_state.resume_text}

Job:
{st.session_state.job_description}

Question:
{q}
"""
        st.write(call_grok(prompt))


# ─────────────────────────────
# COVER LETTER
# ─────────────────────────────
elif st.session_state.tool == "📝 Cover Letter":

    if st.button("Generate"):
        prompt = f"""
Write a professional cover letter.

Resume:
{st.session_state.resume_text}

Job:
{st.session_state.job_description}
"""
        st.write(call_grok(prompt))


# ─────────────────────────────
# INTERVIEW
# ─────────────────────────────
elif st.session_state.tool == "🎤 Interview Prep":

    if st.button("Generate"):
        prompt = f"""
Generate interview questions and answers.

Resume:
{st.session_state.resume_text}

Job:
{st.session_state.job_description}
"""
        st.write(call_grok(prompt))