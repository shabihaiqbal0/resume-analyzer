import streamlit as st
import anthropic
import pdfplumber
import re
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from io import BytesIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base ── */
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  html, body, [class*="css"] {
      font-family: 'DM Sans', sans-serif;
  }

  /* ── Background ── */
  .stApp {
      background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 40%, #0d1f3c 100%);
      background-attachment: fixed;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: rgba(10, 16, 35, 0.95) !important;
      border-right: 1px solid rgba(99, 179, 237, 0.15);
  }
  [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

  /* ── Headings ── */
  h1, h2, h3 {
      font-family: 'Syne', sans-serif !important;
      letter-spacing: -0.02em;
  }
  h1 { color: #f0f9ff !important; font-size: 2.6rem !important; font-weight: 800 !important; }
  h2 { color: #bae6fd !important; font-size: 1.5rem !important; }
  h3 { color: #93c5fd !important; }

  /* ── Cards ── */
  .card {
      background: rgba(14, 25, 50, 0.85);
      border: 1px solid rgba(99, 179, 237, 0.18);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 16px;
      backdrop-filter: blur(12px);
  }
  .card-accent {
      border-left: 4px solid #38bdf8;
  }

  /* ── Metric boxes ── */
  .metric-box {
      background: linear-gradient(135deg, rgba(14,25,50,0.9) 0%, rgba(15,30,65,0.9) 100%);
      border: 1px solid rgba(56,189,248,0.25);
      border-radius: 14px;
      padding: 20px;
      text-align: center;
      transition: transform .2s, box-shadow .2s;
  }
  .metric-box:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(56,189,248,0.15); }
  .metric-value {
      font-family: 'Syne', sans-serif;
      font-size: 2.8rem;
      font-weight: 800;
      background: linear-gradient(90deg, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1;
  }
  .metric-label {
      color: #94a3b8;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-top: 6px;
  }

  /* ── Score ring ── */
  .score-ring-wrap { display: flex; justify-content: center; align-items: center; padding: 10px 0; }

  /* ── Text area fix – visible text + highlight ── */
  textarea {
      background-color: #0f1e3d !important;
      color: #e2e8f0 !important;
      border: 1.5px solid rgba(56,189,248,0.45) !important;
      border-radius: 10px !important;
      font-family: 'DM Sans', sans-serif !important;
      font-size: 0.92rem !important;
      caret-color: #38bdf8 !important;
  }
  textarea:focus {
      border-color: #38bdf8 !important;
      box-shadow: 0 0 0 3px rgba(56,189,248,0.18) !important;
      outline: none !important;
  }

  /* ── File uploader ── */
  [data-testid="stFileUploader"] {
      background: rgba(14, 25, 50, 0.7) !important;
      border: 2px dashed rgba(56,189,248,0.4) !important;
      border-radius: 14px !important;
      padding: 10px !important;
      transition: border-color .2s;
  }
  [data-testid="stFileUploader"]:hover { border-color: #38bdf8 !important; }

  /* ── Buttons ── */
  .stButton > button {
      background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
      color: #fff !important;
      border: none !important;
      border-radius: 10px !important;
      font-family: 'Syne', sans-serif !important;
      font-weight: 700 !important;
      letter-spacing: 0.04em !important;
      padding: 10px 28px !important;
      transition: opacity .2s, transform .15s !important;
  }
  .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab"] {
      color: #64748b !important;
      font-family: 'Syne', sans-serif !important;
      font-weight: 600 !important;
  }
  .stTabs [aria-selected="true"] {
      color: #38bdf8 !important;
      border-bottom: 2px solid #38bdf8 !important;
  }

  /* ── Progress bar ── */
  .stProgress > div > div { background: linear-gradient(90deg, #0ea5e9, #818cf8) !important; border-radius: 99px; }

  /* ── Chat bubbles ── */
  .bubble-user {
      background: linear-gradient(135deg, #1e3a5f, #1e2a5e);
      border: 1px solid rgba(56,189,248,0.25);
      border-radius: 16px 16px 4px 16px;
      padding: 14px 18px;
      margin: 8px 0 8px 40px;
      color: #e2e8f0;
      font-size: 0.92rem;
      position: relative;
  }
  .bubble-user::before {
      content: '👤';
      position: absolute;
      left: -34px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.2rem;
  }
  .bubble-ai {
      background: linear-gradient(135deg, rgba(14,25,50,0.9), rgba(15,22,45,0.9));
      border: 1px solid rgba(99,102,241,0.3);
      border-radius: 16px 16px 16px 4px;
      padding: 14px 18px;
      margin: 8px 40px 8px 0;
      color: #cbd5e1;
      font-size: 0.92rem;
      position: relative;
  }
  .bubble-ai::before {
      content: '🎯';
      position: absolute;
      right: -34px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.2rem;
  }
  .bubble-time {
      font-size: 0.68rem;
      color: #475569;
      margin-top: 4px;
      text-align: right;
  }

  /* ── Tag pills ── */
  .tag-match {
      display: inline-block;
      background: rgba(16,185,129,0.2);
      border: 1px solid rgba(16,185,129,0.5);
      color: #6ee7b7;
      border-radius: 99px;
      padding: 3px 12px;
      font-size: 0.78rem;
      margin: 3px;
  }
  .tag-miss {
      display: inline-block;
      background: rgba(239,68,68,0.15);
      border: 1px solid rgba(239,68,68,0.4);
      color: #fca5a5;
      border-radius: 99px;
      padding: 3px 12px;
      font-size: 0.78rem;
      margin: 3px;
  }
  .tag-partial {
      display: inline-block;
      background: rgba(245,158,11,0.15);
      border: 1px solid rgba(245,158,11,0.4);
      color: #fcd34d;
      border-radius: 99px;
      padding: 3px 12px;
      font-size: 0.78rem;
      margin: 3px;
  }

  /* ── Divider ── */
  hr { border-color: rgba(99,179,237,0.1) !important; }

  /* ── Input labels ── */
  label, .stTextArea label, .stFileUploader label {
      color: #93c5fd !important;
      font-family: 'Syne', sans-serif !important;
      font-weight: 600 !important;
      font-size: 0.85rem !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
  }

  /* ── Expander ── */
  details { border: 1px solid rgba(56,189,248,0.15) !important; border-radius: 10px !important; }
  summary { color: #7dd3fc !important; font-family: 'Syne', sans-serif !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 99px; }

  /* ── Select / radio ── */
  .stSelectbox > div, .stRadio > div { color: #cbd5e1 !important; }

  /* ── General text ── */
  p, li, span, div { color: #cbd5e1; }
  .stMarkdown p { color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "chat_history": [],           # [{role, content, timestamp}]
    "analysis_result": None,
    "resume_text": "",
    "job_description": "",
    "analysis_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def extract_pdf_text(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text.strip()


def call_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def analyze_resume(resume_text: str, job_desc: str) -> dict:
    system = """You are an elite Applicant Tracking System (ATS) + career coach AI.
Return ONLY a valid JSON object — no markdown fences, no extra text.
Schema:
{
  "ats_score": <0-100 int>,
  "overall_match": <0-100 int>,
  "section_scores": {"experience": <0-100>, "education": <0-100>, "skills": <0-100>, "formatting": <0-100>, "keywords": <0-100>},
  "matched_keywords": ["...", ...],
  "missing_keywords": ["...", ...],
  "partial_keywords": ["...", ...],
  "strengths": ["...", ...],
  "weaknesses": ["...", ...],
  "action_items": ["...", ...],
  "salary_range": "<estimated range based on role & skills>",
  "role_fit_level": "<Entry / Mid / Senior / Lead / Executive>",
  "interview_questions": ["...", ...],
  "cover_letter_hook": "<one compelling opening paragraph for a cover letter>",
  "linkedin_tips": ["...", ...],
  "summary": "<2-3 sentence overall assessment>"
}"""
    prompt = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
    raw = call_claude(system, prompt, max_tokens=3000)
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


def chat_with_resume(question: str, resume_text: str, job_desc: str, history: list) -> str:
    system = """You are ResumeIQ Pro — an expert career coach AI.
You have access to the candidate's resume and target job description.
Answer questions about fit, improvement tips, interview prep, salary negotiation, or anything career-related.
Be specific, actionable, and warm. Use bullet points where helpful."""

    convo = []
    for h in history[-8:]:   # keep last 8 turns for context
        convo.append({"role": h["role"], "content": h["content"]})
    convo.append({"role": "user", "content": question})

    context_prefix = f"[RESUME]\n{resume_text[:3000]}\n\n[JOB DESCRIPTION]\n{job_desc[:2000]}\n\n"
    convo[0]["content"] = context_prefix + convo[0]["content"]

    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1500,
        system=system,
        messages=convo,
    )
    return msg.content[0].text


def score_color(score: int) -> str:
    if score >= 80: return "#10b981"
    if score >= 60: return "#f59e0b"
    return "#ef4444"


def make_radar(section_scores: dict):
    cats = list(section_scores.keys())
    vals = list(section_scores.values())
    cats_display = [c.capitalize() for c in cats]

    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats_display + [cats_display[0]],
        fill='toself',
        fillcolor='rgba(56,189,248,0.15)',
        line=dict(color='#38bdf8', width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(99,179,237,0.15)', color='#475569'),
            angularaxis=dict(gridcolor='rgba(99,179,237,0.1)', color='#94a3b8'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=30, b=30),
        height=280,
        showlegend=False,
    )
    return fig


def make_gauge(score: int, label: str):
    color = score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title=dict(text=label, font=dict(color="#94a3b8", size=13, family="Syne")),
        number=dict(font=dict(color=color, size=38, family="Syne"), suffix="/100"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor='#475569', tickfont=dict(color='#475569')),
            bar=dict(color=color),
            bgcolor='rgba(15,25,50,0.6)',
            bordercolor='rgba(56,189,248,0.15)',
            steps=[
                dict(range=[0, 40], color='rgba(239,68,68,0.08)'),
                dict(range=[40, 70], color='rgba(245,158,11,0.08)'),
                dict(range=[70, 100], color='rgba(16,185,129,0.08)'),
            ],
            threshold=dict(line=dict(color=color, width=3), thickness=0.8, value=score),
        ),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=15, r=15, t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px'>
      <div style='font-family:Syne;font-size:1.6rem;font-weight:800;
                  background:linear-gradient(90deg,#38bdf8,#818cf8);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        🎯 ResumeIQ Pro
      </div>
      <div style='color:#475569;font-size:0.75rem;letter-spacing:.1em;margin-top:4px;'>
        AI-POWERED CAREER INTELLIGENCE
      </div>
    </div>
    <hr style='border-color:rgba(56,189,248,0.1);margin:10px 0 20px;'>
    """, unsafe_allow_html=True)

    st.markdown("### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF only",
        type=["pdf"],
        help="Upload your resume as a PDF file",
    )

    if uploaded_file:
        st.session_state.resume_text = extract_pdf_text(BytesIO(uploaded_file.read()))
        st.success(f"✅ Loaded — {len(st.session_state.resume_text.split())} words")

    st.markdown("---")
    st.markdown("### 🧰 Tools")
    tool = st.radio(
        "Select tool",
        ["📊 Deep Analysis", "💬 AI Career Chat", "📝 Cover Letter", "🎤 Interview Prep"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.session_state.analysis_done and st.session_state.analysis_result:
        r = st.session_state.analysis_result
        st.markdown("### 📈 Quick Stats")
        col1, col2 = st.columns(2)
        col1.metric("ATS Score", f"{r['ats_score']}%")
        col2.metric("Match", f"{r['overall_match']}%")
        st.caption(f"Role fit: **{r.get('role_fit_level', 'N/A')}**")
        st.caption(f"Est. salary: {r.get('salary_range', 'N/A')}")

    st.markdown("---")
    st.markdown(
        "<div style='color:#334155;font-size:0.7rem;text-align:center;'>Powered by Claude AI</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  MAIN HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding: 30px 0 10px'>
  <h1>🎯 ResumeIQ Pro</h1>
  <p style='color:#64748b;font-size:1rem;margin-top:-8px;'>
    World-class resume analysis, ATS scoring, and career coaching — powered by AI.
  </p>
</div>
""", unsafe_allow_html=True)

# Job description input (always visible, highlighted)
jd_col, _ = st.columns([2, 1])
with jd_col:
    st.markdown("### 📋 Job Description")
    job_desc_input = st.text_area(
        "Paste the full job description here",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste the job description you're targeting here.\nThe more detail you provide, the more precise the analysis...",
        help="Paste the complete job description for the role you're applying for",
    )
    st.session_state.job_description = job_desc_input

st.markdown("---")


# ─────────────────────────────────────────────
#  TOOL: DEEP ANALYSIS
# ─────────────────────────────────────────────
if "📊 Deep Analysis" in tool:
    st.markdown("## 📊 Deep Resume Analysis")

    can_analyze = bool(st.session_state.resume_text) and bool(st.session_state.job_description)

    if not st.session_state.resume_text:
        st.info("👈 Upload your resume PDF from the sidebar to get started.")
    if not st.session_state.job_description:
        st.info("☝️ Paste a job description above to enable analysis.")

    if can_analyze:
        if st.button("🚀 Run Full Analysis", use_container_width=False):
            with st.spinner("Analyzing your resume with AI..."):
                try:
                    result = analyze_resume(
                        st.session_state.resume_text,
                        st.session_state.job_description,
                    )
                    st.session_state.analysis_result = result
                    st.session_state.analysis_done = True
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    if st.session_state.analysis_done and st.session_state.analysis_result:
        r = st.session_state.analysis_result

        # ── Score row ──
        st.markdown("### 🏆 Scores")
        c1, c2, c3, c4, c5 = st.columns(5)
        metrics = [
            ("ATS Score", r["ats_score"]),
            ("Overall Match", r["overall_match"]),
            ("Experience", r["section_scores"]["experience"]),
            ("Skills", r["section_scores"]["skills"]),
            ("Keywords", r["section_scores"]["keywords"]),
        ]
        for col, (label, val) in zip([c1, c2, c3, c4, c5], metrics):
            col.markdown(f"""
            <div class='metric-box'>
              <div class='metric-value' style='background:linear-gradient(90deg,{score_color(val)},{score_color(val)}88);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{val}</div>
              <div class='metric-label'>{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Gauges + Radar ──
        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            st.plotly_chart(make_gauge(r["ats_score"], "ATS Score"), use_container_width=True, config={"displayModeBar": False})
        with gc2:
            st.plotly_chart(make_gauge(r["overall_match"], "Job Match"), use_container_width=True, config={"displayModeBar": False})
        with gc3:
            st.plotly_chart(make_radar(r["section_scores"]), use_container_width=True, config={"displayModeBar": False})

        st.markdown("---")

        # ── Keywords ──
        st.markdown("### 🔑 Keyword Analysis")
        kc1, kc2, kc3 = st.columns(3)

        with kc1:
            st.markdown("**✅ Matched Keywords**")
            html = "".join(f"<span class='tag-match'>{k}</span>" for k in r.get("matched_keywords", []))
            st.markdown(html or "<span style='color:#475569'>None found</span>", unsafe_allow_html=True)

        with kc2:
            st.markdown("**⚠️ Partial / Synonyms**")
            html = "".join(f"<span class='tag-partial'>{k}</span>" for k in r.get("partial_keywords", []))
            st.markdown(html or "<span style='color:#475569'>None found</span>", unsafe_allow_html=True)

        with kc3:
            st.markdown("**❌ Missing Keywords**")
            html = "".join(f"<span class='tag-miss'>{k}</span>" for k in r.get("missing_keywords", []))
            st.markdown(html or "<span style='color:#475569'>None missing</span>", unsafe_allow_html=True)

        st.markdown("---")

        # ── Strengths / Weaknesses ──
        sw1, sw2 = st.columns(2)
        with sw1:
            st.markdown("### 💪 Strengths")
            for s in r.get("strengths", []):
                st.markdown(f"<div class='card card-accent'>✅ {s}</div>", unsafe_allow_html=True)
        with sw2:
            st.markdown("### 🔧 Areas to Improve")
            for w in r.get("weaknesses", []):
                st.markdown(f"<div class='card' style='border-left:4px solid #f59e0b;'>⚠️ {w}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # ── Action items ──
        st.markdown("### ✅ Priority Action Items")
        for i, action in enumerate(r.get("action_items", []), 1):
            st.markdown(
                f"<div class='card' style='border-left:4px solid #818cf8;'><b style='color:#a5b4fc;'>#{i}</b> &nbsp;{action}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Summary + meta ──
        mc1, mc2 = st.columns([3, 1])
        with mc1:
            st.markdown("### 📝 AI Summary")
            st.markdown(f"<div class='card'>{r.get('summary','')}</div>", unsafe_allow_html=True)
        with mc2:
            st.markdown("### 💰 Insights")
            st.markdown(f"<div class='card'><b style='color:#7dd3fc;'>Salary Range</b><br>{r.get('salary_range','N/A')}<br><br><b style='color:#7dd3fc;'>Role Fit Level</b><br>{r.get('role_fit_level','N/A')}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TOOL: AI CAREER CHAT
# ─────────────────────────────────────────────
elif "💬 AI Career Chat" in tool:
    st.markdown("## 💬 AI Career Chat")
    st.caption("Ask anything about your resume, the role, interview prep, salary, or career strategy.")

    if not st.session_state.resume_text:
        st.warning("Please upload your resume first.")
    else:
        # ── Message history ──
        if st.session_state.chat_history:
            st.markdown("### 🗨️ Conversation")
            for msg in st.session_state.chat_history:
                ts = msg.get("timestamp", "")
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class='bubble-user'>
                      {msg['content']}
                      <div class='bubble-time'>{ts}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='bubble-ai'>
                      {msg['content']}
                      <div class='bubble-time'>{ts}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Input ──
        with st.form("chat_form", clear_on_submit=True):
            user_msg = st.text_area(
                "Your message",
                placeholder="e.g. How well do I match this role? What should I improve first? How do I negotiate salary?",
                height=100,
            )
            submitted = st.form_submit_button("Send ➤", use_container_width=True)

        if submitted and user_msg.strip():
            ts = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_msg,
                "timestamp": ts,
            })
            with st.spinner("ResumeIQ is thinking..."):
                reply = chat_with_resume(
                    user_msg,
                    st.session_state.resume_text,
                    st.session_state.job_description,
                    st.session_state.chat_history,
                )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": reply,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            st.rerun()

        if st.session_state.chat_history:
            if st.button("🗑️ Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

        # Quick prompts
        st.markdown("**💡 Quick prompts:**")
        qcols = st.columns(3)
        prompts = [
            "What are my top 3 weaknesses for this role?",
            "Rewrite my professional summary for this job",
            "What salary should I negotiate for?",
            "Give me 5 likely interview questions",
            "How can I improve my ATS score?",
            "What skills should I learn next?",
        ]
        for i, (col, prompt) in enumerate(zip(qcols * 2, prompts)):
            if col.button(prompt, key=f"qp_{i}"):
                ts = datetime.now().strftime("%H:%M")
                st.session_state.chat_history.append({"role": "user", "content": prompt, "timestamp": ts})
                with st.spinner("Thinking..."):
                    reply = chat_with_resume(prompt, st.session_state.resume_text, st.session_state.job_description, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%H:%M")})
                st.rerun()


# ─────────────────────────────────────────────
#  TOOL: COVER LETTER
# ─────────────────────────────────────────────
elif "📝 Cover Letter" in tool:
    st.markdown("## 📝 AI Cover Letter Generator")

    if not st.session_state.resume_text or not st.session_state.job_description:
        st.warning("Please upload your resume and paste a job description first.")
    else:
        tone = st.select_slider(
            "Letter tone",
            options=["Formal", "Professional", "Confident", "Enthusiastic", "Creative"],
            value="Professional",
        )
        word_count = st.slider("Target word count", 200, 600, 350, step=50)

        if st.button("✨ Generate Cover Letter"):
            with st.spinner("Crafting your cover letter..."):
                system = f"""You are an expert career writer. Write a compelling cover letter.
Tone: {tone}. Target length: ~{word_count} words.
Use the candidate's actual experience from their resume.
Structure: Opening hook → Why this role → Relevant achievements → Cultural fit → CTA closing.
Do NOT add placeholder brackets like [Company Name] — infer from job description."""

                prompt = f"RESUME:\n{st.session_state.resume_text[:3000]}\n\nJOB DESCRIPTION:\n{st.session_state.job_description[:2000]}"
                cover_letter = call_claude(system, prompt, max_tokens=1200)

            st.markdown("### Your Cover Letter")
            st.markdown(f"<div class='card'>{cover_letter.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download as .txt", cover_letter, file_name="cover_letter.txt")

        if st.session_state.analysis_result and st.session_state.analysis_result.get("cover_letter_hook"):
            with st.expander("💡 AI-suggested opening hook"):
                st.write(st.session_state.analysis_result["cover_letter_hook"])


# ─────────────────────────────────────────────
#  TOOL: INTERVIEW PREP
# ─────────────────────────────────────────────
elif "🎤 Interview Prep" in tool:
    st.markdown("## 🎤 Interview Preparation")

    if not st.session_state.resume_text or not st.session_state.job_description:
        st.warning("Please upload your resume and paste a job description first.")
    else:
        interview_type = st.selectbox(
            "Interview type",
            ["Behavioral (STAR)", "Technical", "Case Study", "Culture Fit", "Executive / Leadership"],
        )
        num_questions = st.slider("Number of questions", 5, 15, 8)

        if st.button("🎯 Generate Interview Questions + Answers"):
            with st.spinner("Preparing your interview guide..."):
                system = f"""You are an expert interview coach.
Generate {num_questions} {interview_type} interview questions tailored to this candidate + role.
For each question, provide:
1. The question
2. Why this question will be asked (interviewer's intent)
3. A strong sample answer framework using the candidate's actual background.
Format with clear headers per question."""

                prompt = f"RESUME:\n{st.session_state.resume_text[:3000]}\n\nJOB DESCRIPTION:\n{st.session_state.job_description[:2000]}"
                guide = call_claude(system, prompt, max_tokens=3000)

            st.markdown("### 🗂️ Your Interview Guide")
            st.markdown(f"<div class='card' style='white-space:pre-wrap;line-height:1.8;'>{guide}</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Interview Guide", guide, file_name="interview_prep.txt")

        if st.session_state.analysis_result:
            qs = st.session_state.analysis_result.get("interview_questions", [])
            if qs:
                with st.expander("⚡ Quick questions from analysis"):
                    for q in qs:
                        st.markdown(f"• {q}")