import streamlit as st
import pdfplumber
import re
import json
import requests

st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #050508 !important;
    color: #f0f0ff !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(120,80,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(56,189,248,0.08) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: rgba(8,8,16,0.98) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div { padding: 0 1.2rem !important; }

.sidebar-brand {
    padding: 1.8rem 0.3rem 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.2rem;
}
.sidebar-logo {
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-tagline {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.25);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.2rem;
}
.sidebar-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.25);
    margin: 1rem 0 0.5rem;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(167,139,250,0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] * { color: rgba(255,255,255,0.5) !important; font-size: 0.82rem !important; }
.stFileUploader label { display: none !important; }

.stRadio > div { gap: 2px !important; }
.stRadio label {
    padding: 0.6rem 0.8rem !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.45) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stRadio label:hover { background: rgba(255,255,255,0.05) !important; color: rgba(255,255,255,0.85) !important; }
[data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.25) !important; font-size: 0.65rem !important; text-transform: uppercase !important; letter-spacing: 2px !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    margin-top: 0.3rem !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 30px rgba(124,58,237,0.4) !important; }

.stTextArea textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    color: rgba(255,255,255,0.88) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    padding: 1rem 1.2rem !important;
    transition: all 0.3s !important;
}
.stTextArea textarea:focus { border-color: rgba(124,58,237,0.5) !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important; }
.stTextArea textarea::placeholder { color: rgba(255,255,255,0.18) !important; }
.stTextArea label { display: none !important; }

.stTextInput input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.88) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput label { display: none !important; }

.stSuccess > div { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 10px !important; color: #6ee7b7 !important; }
.stWarning > div { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 10px !important; color: #fcd34d !important; }
.stInfo > div { background: rgba(56,189,248,0.06) !important; border: 1px solid rgba(56,189,248,0.15) !important; border-radius: 10px !important; color: #7dd3fc !important; }

.main-wrap { position: relative; z-index: 1; }

.hero-section {
    padding: 3.5rem 4rem 2.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(167,139,250,0.1);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.7rem;
    font-weight: 600;
    color: #c4b5fd;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 1.3rem;
}
.hero-title {
    font-size: clamp(2.2rem, 4vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -1.5px;
    color: #fff;
    margin-bottom: 0.9rem;
}
.hero-title span {
    background: linear-gradient(135deg, #a78bfa, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.38);
    line-height: 1.65;
    max-width: 500px;
    margin-bottom: 2rem;
}
.stats-row { display: flex; gap: 2.5rem; flex-wrap: wrap; }
.stat-num {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.stat-label { font-size: 0.68rem; color: rgba(255,255,255,0.28); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; }

.content-section { padding: 2.5rem 4rem 4rem; }

.section-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2.5px; color: rgba(255,255,255,0.22); margin-bottom: 0.35rem; }
.section-heading { font-size: 1.25rem; font-weight: 700; color: rgba(255,255,255,0.88); letter-spacing: -0.5px; margin-bottom: 1rem; }

.score-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(37,99,235,0.08));
    border: 1px solid rgba(124,58,237,0.22);
    border-radius: 24px;
    padding: 2.5rem;
    text-align: center;
    margin: 1.5rem 0;
}
.score-value {
    font-size: 5.5rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -4px;
    margin-bottom: 0.3rem;
}
.score-sublabel { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 3px; color: rgba(255,255,255,0.28); margin-bottom: 1rem; }
.score-badge { display: inline-block; padding: 0.38rem 1.1rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }

.result-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.result-card:hover { border-color: rgba(255,255,255,0.1); }
.result-card-title {
    font-size: 0.63rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 0.9rem;
}
.result-card-body { font-size: 0.9rem; color: rgba(255,255,255,0.6); line-height: 1.75; }

.tag { display: inline-flex; align-items: center; padding: 0.3rem 0.85rem; border-radius: 8px; font-size: 0.8rem; font-weight: 500; margin: 0.22rem; }
.tag-green { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #6ee7b7; }
.tag-red { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: #fca5a5; }

.tip-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: rgba(255,255,255,0.6);
    font-size: 0.88rem;
    line-height: 1.65;
}
.tip-row:last-child { border-bottom: none; }
.tip-num {
    min-width: 22px; height: 22px;
    background: rgba(124,58,237,0.18);
    border: 1px solid rgba(124,58,237,0.28);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; color: #a78bfa;
    flex-shrink: 0; margin-top: 2px;
}

.chat-output {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    color: rgba(255,255,255,0.72);
    font-size: 0.9rem;
    line-height: 1.8;
    white-space: pre-wrap;
    margin-top: 1rem;
}

.sidebar-footer {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.18);
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in {"resume_text": "", "job_description": "", "tool": "📊 Deep Analysis", "analysis_result": None, "use_demo": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── DEMO DATA ──
DEMO_RESUME = """Ahmed Khan | Senior Software Engineer
ahmed.khan@email.com | linkedin.com/in/ahmedkhan

EXPERIENCE
Senior Software Engineer — TechVentures Inc. (2021–Present)
• Architected microservices platform handling 2M+ daily requests (Python, FastAPI)
• Led team of 6 engineers, reduced API latency by 65% via Redis caching
• Built CI/CD pipelines cutting deployment time from 2hrs to 15 mins

Software Engineer — DataFlow Systems (2019–2021)
• Built real-time analytics dashboard (React, D3.js) for 50K+ users
• Developed ETL pipelines processing 10GB+ daily data using Apache Spark

SKILLS: Python, JavaScript, React, FastAPI, AWS, Docker, Kubernetes, PostgreSQL, Redis

EDUCATION: BS Computer Science — FAST University (2019) | GPA 3.8/4.0
CERTIFICATIONS: AWS Solutions Architect | Google Cloud Professional"""

DEMO_JOB = """Senior Software Engineer — Remote | $120K–$160K
Requirements: 4+ years experience, Python or Go, microservices, React, AWS, Docker/Kubernetes, strong SQL, team leadership.
Nice to have: Kafka, ML pipelines, open source contributions."""

# ── API ──
def call_grok(prompt):
    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {st.secrets['GROK_API_KEY']}", "Content-Type": "application/json"},
            json={"model": "grok-2-latest", "messages": [
                {"role": "system", "content": "You are a world-class career coach and resume expert with 20 years at top tech companies."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.7},
            timeout=40,
        )
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()

def analyze_resume(resume, job):
    prompt = f"""Analyze this resume vs job description. Return ONLY valid JSON, no markdown, no extra text:
{{"ats_score":<0-100>,"match_level":"<Excellent|Strong|Moderate|Weak>","summary":"<2-3 sentence assessment>","strengths":["<strength>","<strength>","<strength>","<strength>"],"missing_skills":["<gap>","<gap>","<gap>"],"tips":["<tip>","<tip>","<tip>","<tip>"]}}
RESUME: {resume[:3500]}
JOB: {job[:2000]}"""
    raw = re.sub(r"```json|```", "", call_grok(prompt)).strip()
    try:
        return json.loads(raw)
    except:
        try:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m: return json.loads(m.group())
        except: pass
        return {"ats_score": 0, "match_level": "Unknown", "summary": "Could not parse. Please try again.", "strengths": [], "missing_skills": [], "tips": []}

# ══════════════════════════════
# SIDEBAR
# ══════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-logo">⚡ ResumeIQ Pro</div><div class="sidebar-tagline">AI-Powered Career Intelligence</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">📄 Your Resume (PDF)</div>', unsafe_allow_html=True)
    file = st.file_uploader("", type=["pdf"])
    if file:
        st.session_state.resume_text = extract_pdf(file)
        st.session_state.use_demo = False
        st.success("✅ Resume loaded!")

    st.markdown('<div class="sidebar-label">🎮 Quick Start</div>', unsafe_allow_html=True)
    if st.button("Try Sample Resume"):
        st.session_state.resume_text = DEMO_RESUME
        st.session_state.use_demo = True
    if st.session_state.use_demo:
        st.info("Sample resume active")

    st.markdown('<div class="sidebar-label">🛠 Tools</div>', unsafe_allow_html=True)
    st.session_state.tool = st.radio("", ["📊 Deep Analysis", "💬 Career Chat", "📝 Cover Letter", "🎤 Interview Prep"], label_visibility="collapsed")

    st.markdown('<div class="sidebar-footer">ResumeIQ Pro · Powered by Grok AI</div>', unsafe_allow_html=True)

# ══════════════════════════════
# HERO
# ══════════════════════════════
st.markdown("""
<div class="main-wrap">
<div class="hero-section">
    <div class="eyebrow">⚡ Powered by Grok AI</div>
    <div class="hero-title">Get hired faster with<br><span>AI resume analysis</span></div>
    <div class="hero-sub">Upload your CV, paste the job description, and get your match score, strengths, skill gaps, and actionable tips — in seconds.</div>
    <div class="stats-row">
        <div><div class="stat-num">98%</div><div class="stat-label">Accuracy</div></div>
        <div><div class="stat-num">&lt;10s</div><div class="stat-label">Analysis Time</div></div>
        <div><div class="stat-num">ATS</div><div class="stat-label">Optimized</div></div>
        <div><div class="stat-num">4-in-1</div><div class="stat-label">Career Tools</div></div>
    </div>
</div>
<div class="content-section">
""", unsafe_allow_html=True)

# ── JOB INPUT ──
st.markdown('<div class="section-label">Step 1</div><div class="section-heading">Paste the Job Description</div>', unsafe_allow_html=True)
job = st.text_area("", value=DEMO_JOB if st.session_state.use_demo else "", height=150, placeholder="Paste the full job description here...")
st.session_state.job_description = job
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════
# DEEP ANALYSIS
# ══════════════════════════════
if st.session_state.tool == "📊 Deep Analysis":
    st.markdown('<div class="section-label">Step 2</div><div class="section-heading">Run Your Analysis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        clicked = st.button("🚀 Analyze My Resume", use_container_width=True)

    if clicked:
        if not st.session_state.resume_text:
            st.warning("⚠️ Upload your resume PDF or click 'Try Sample Resume' in the sidebar.")
        elif not st.session_state.job_description.strip():
            st.warning("⚠️ Please paste a job description above.")
        else:
            with st.spinner("Analyzing your resume..."):
                st.session_state.analysis_result = analyze_resume(st.session_state.resume_text, st.session_state.job_description)

    r = st.session_state.analysis_result
    if r and r.get("ats_score", 0) > 0:
        score = r.get("ats_score", 0)
        if score >= 75:
            sc = "linear-gradient(135deg,#34d399,#059669)"; bb = "rgba(16,185,129,0.12)"; bo = "rgba(16,185,129,0.25)"; bc = "#6ee7b7"; bt = "✦ Excellent Match"
        elif score >= 55:
            sc = "linear-gradient(135deg,#fbbf24,#d97706)"; bb = "rgba(245,158,11,0.12)"; bo = "rgba(245,158,11,0.25)"; bc = "#fcd34d"; bt = "◈ Strong Match"
        elif score >= 40:
            sc = "linear-gradient(135deg,#fb923c,#ea580c)"; bb = "rgba(251,146,60,0.12)"; bo = "rgba(251,146,60,0.25)"; bc = "#fdba74"; bt = "◇ Moderate Match"
        else:
            sc = "linear-gradient(135deg,#f87171,#dc2626)"; bb = "rgba(239,68,68,0.12)"; bo = "rgba(239,68,68,0.25)"; bc = "#fca5a5"; bt = "○ Needs Work"

        st.markdown(f"""
        <div class="score-card">
            <div class="score-value" style="background:{sc};-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{score}%</div>
            <div class="score-sublabel">ATS Match Score</div>
            <span class="score-badge" style="background:{bb};border:1px solid {bo};color:{bc};">{bt}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="result-card"><div class="result-card-title" style="color:rgba(167,139,250,0.8);">📋 Assessment</div><div class="result-card-body">{r.get("summary","")}</div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            tags = "".join([f'<span class="tag tag-green">✓ {s}</span>' for s in r.get("strengths", [])])
            st.markdown(f'<div class="result-card"><div class="result-card-title" style="color:#6ee7b7;">💪 Strengths</div>{tags}</div>', unsafe_allow_html=True)
        with c2:
            tags = "".join([f'<span class="tag tag-red">✗ {g}</span>' for g in r.get("missing_skills", [])])
            st.markdown(f'<div class="result-card"><div class="result-card-title" style="color:#fca5a5;">⚠️ Skill Gaps</div>{tags}</div>', unsafe_allow_html=True)

        tips = r.get("tips", [])
        if tips:
            tips_html = "".join([f'<div class="tip-row"><span class="tip-num">{i+1}</span><span>{t}</span></div>' for i, t in enumerate(tips)])
            st.markdown(f'<div class="result-card"><div class="result-card-title" style="color:#7dd3fc;">🚀 Improvement Roadmap</div>{tips_html}</div>', unsafe_allow_html=True)

# ══════════════════════════════
# CAREER CHAT
# ══════════════════════════════
elif st.session_state.tool == "💬 Career Chat":
    st.markdown('<div class="section-heading">Ask Your AI Career Coach</div>', unsafe_allow_html=True)
    q = st.text_area("", height=80, placeholder="e.g. How should I rewrite my summary? What skills should I add? How do I negotiate salary?")
    if st.button("💬 Ask Career Coach"):
        if not st.session_state.resume_text:
            st.warning("Please upload your resume or use the sample resume first.")
        elif not q.strip():
            st.warning("Please type your question.")
        else:
            with st.spinner("Thinking..."):
                result = call_grok(f"Resume:\n{st.session_state.resume_text[:3000]}\n\nJob:\n{st.session_state.job_description[:1500]}\n\nQuestion: {q}\n\nAnswer professionally and specifically.")
                st.markdown(f'<div class="chat-output">{result}</div>', unsafe_allow_html=True)

# ══════════════════════════════
# COVER LETTER
# ══════════════════════════════
elif st.session_state.tool == "📝 Cover Letter":
    st.markdown('<div class="section-heading">Generate a Tailored Cover Letter</div>', unsafe_allow_html=True)
    if st.button("✍️ Generate Cover Letter"):
        if not st.session_state.resume_text:
            st.warning("Please upload your resume or use the sample resume first.")
        elif not st.session_state.job_description.strip():
            st.warning("Please paste a job description above.")
        else:
            with st.spinner("Writing your personalized cover letter..."):
                result = call_grok(f"Write a compelling 3-paragraph cover letter. No clichés. Specific and confident.\n\nResume:\n{st.session_state.resume_text[:3000]}\n\nJob:\n{st.session_state.job_description[:1500]}")
                st.markdown(f'<div class="chat-output">{result}</div>', unsafe_allow_html=True)

# ══════════════════════════════
# INTERVIEW PREP
# ══════════════════════════════
elif st.session_state.tool == "🎤 Interview Prep":
    st.markdown('<div class="section-heading">Prepare for Your Interview</div>', unsafe_allow_html=True)
    if st.button("🎯 Generate Questions & Model Answers"):
        if not st.session_state.resume_text:
            st.warning("Please upload your resume or use the sample resume first.")
        elif not st.session_state.job_description.strip():
            st.warning("Please paste a job description above.")
        else:
            with st.spinner("Preparing your interview questions..."):
                result = call_grok(f"Generate 6 likely interview questions for this role with: 1) The question 2) Why they ask it 3) A strong model answer.\n\nResume:\n{st.session_state.resume_text[:3000]}\n\nJob:\n{st.session_state.job_description[:1500]}")
                st.markdown(f'<div class="chat-output">{result}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)