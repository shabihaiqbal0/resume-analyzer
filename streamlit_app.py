import streamlit as st
import anthropic
import PyPDF2
import docx2txt
import io
import json
import re

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --bg: #0f0e17;
    --surface: #1a1928;
    --accent: #ff6b35;
    --accent2: #f7c59f;
    --text: #fffffe;
    --muted: #a7a9be;
    --card: #1f1e2e;
    --border: #2e2d3d;
    --success: #2cb67d;
    --warn: #f5a623;
    --danger: #ef4565;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Header */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 400;
    color: var(--text);
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero h1 span { color: var(--accent); font-style: italic; }
.hero p {
    color: var(--muted);
    font-size: 1.1rem;
    font-weight: 300;
    max-width: 500px;
    margin: 0 auto;
}

/* Upload zone */
.upload-section {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: border-color 0.2s;
}
.upload-section:hover { border-color: var(--accent); }

/* Score ring */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
}
.score-ring {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    font-weight: 400;
    margin-bottom: 0.75rem;
    position: relative;
}
.score-high  { background: conic-gradient(var(--success) var(--pct), var(--border) 0); color: var(--success); }
.score-mid   { background: conic-gradient(var(--warn) var(--pct), var(--border) 0); color: var(--warn); }
.score-low   { background: conic-gradient(var(--danger) var(--pct), var(--border) 0); color: var(--danger); }
.score-inner {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background: var(--card);
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
}
.score-label {
    font-size: 1rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}

/* Skill tags */
.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 3px;
}
.tag-skill  { background: rgba(255,107,53,0.15); color: var(--accent); border: 1px solid rgba(255,107,53,0.3); }
.tag-miss   { background: rgba(239,69,101,0.15); color: var(--danger); border: 1px solid rgba(239,69,101,0.3); }
.tag-strong { background: rgba(44,182,125,0.15); color: var(--success); border: 1px solid rgba(44,182,125,0.3); }

/* Cards */
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.stat-card h4 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: var(--accent2);
    margin: 0 0 0.5rem;
}
.stat-card p { color: var(--muted); font-size: 0.9rem; margin: 0; line-height: 1.6; }

/* Bullet items */
.bullet-item {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
    color: var(--muted);
    line-height: 1.5;
}
.bullet-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
    margin-top: 6px;
}

/* Section titles */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    color: var(--text);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Override Streamlit widgets */
.stFileUploader > div {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}
.stTextArea textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

div[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'DM Serif Display', serif !important; }
div[data-testid="stMetricLabel"] { color: var(--muted) !important; }

.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def analyze_resume(resume_text: str, job_description: str) -> dict:
    client = anthropic.Anthropic()

    jd_section = f"\n\nJob Description:\n{job_description}" if job_description.strip() else ""

    prompt = f"""You are an expert resume analyst and career coach. Analyze the following resume{' against the job description' if jd_section else ''} and return a detailed JSON report.

Resume:
{resume_text}{jd_section}

Return ONLY a valid JSON object (no markdown, no backticks) with this exact structure:
{{
  "overall_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "sections": {{
    "contact_info": {{"score": <0-100>, "feedback": "<feedback>"}},
    "work_experience": {{"score": <0-100>, "feedback": "<feedback>"}},
    "education": {{"score": <0-100>, "feedback": "<feedback>"}},
    "skills": {{"score": <0-100>, "feedback": "<feedback>"}},
    "formatting": {{"score": <0-100>, "feedback": "<feedback>"}}
  }},
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "improvements": ["<improvement1>", "<improvement2>", "<improvement3>", "<improvement4>"],
  "skills_found": ["<skill1>", "<skill2>", "..."],
  "skills_missing": ["<missing1>", "<missing2>", "..."],
  "ats_score": <integer 0-100>,
  "ats_tips": ["<tip1>", "<tip2>", "<tip3>"],
  "action_items": ["<action1>", "<action2>", "<action3>"]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def score_class(score: int) -> str:
    if score >= 70: return "score-high"
    if score >= 40: return "score-mid"
    return "score-low"


def render_score_ring(score: int, label: str):
    cls = score_class(score)
    pct = f"{score * 3.6}deg"
    st.markdown(f"""
    <div class="score-container">
      <div class="score-ring {cls}" style="--pct:{pct}">
        <div class="score-inner">{score}</div>
      </div>
      <div class="score-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_tags(items: list, tag_class: str):
    html = "".join(f'<span class="tag {tag_class}">{item}</span>' for item in items)
    st.markdown(f'<div style="margin:0.5rem 0">{html}</div>', unsafe_allow_html=True)


def render_bullets(items: list):
    html = "".join(
        f'<div class="bullet-item"><div class="bullet-dot"></div><span>{item}</span></div>'
        for item in items
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── App ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Resume <span>Analyzer</span></h1>
  <p>AI-powered feedback to land your next role</p>
</div>
""", unsafe_allow_html=True)

# Input columns
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("#### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF or DOCX", type=["pdf", "docx"],
        label_visibility="collapsed"
    )

with col_right:
    st.markdown("#### 💼 Job Description *(optional)*")
    job_desc = st.text_area(
        "Paste the job description",
        placeholder="Paste the job description here for a tailored analysis...",
        height=160,
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_btn = st.button("✦ Analyze Resume", disabled=uploaded_file is None)

# ─── Analysis ───────────────────────────────────────────────────────────────
if analyze_btn and uploaded_file:
    file_bytes = uploaded_file.read()

    with st.spinner("Reading your resume..."):
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = extract_text_from_docx(file_bytes)

    if not resume_text.strip():
        st.error("Could not extract text from the file. Please try a different format.")
        st.stop()

    with st.spinner("Analyzing with AI — this takes a few seconds..."):
        try:
            result = analyze_resume(resume_text, job_desc)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Analysis error: {e}")
            st.stop()

    # ── Score Overview ──
    st.markdown('<div class="section-title">Score Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: render_score_ring(result["overall_score"], "Overall Score")
    with c2: render_score_ring(result["ats_score"], "ATS Score")
    with c3:
        avg_section = int(sum(v["score"] for v in result["sections"].values()) / len(result["sections"]))
        render_score_ring(avg_section, "Section Avg")

    # ── Summary ──
    st.markdown(f"""
    <div class="stat-card" style="margin-top:1.5rem">
      <h4>Summary</h4>
      <p>{result['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Section Scores ──
    st.markdown('<div class="section-title">Section Breakdown</div>', unsafe_allow_html=True)
    sec_cols = st.columns(len(result["sections"]))
    icons = {"contact_info": "👤", "work_experience": "💼", "education": "🎓", "skills": "⚡", "formatting": "✦"}
    for i, (key, val) in enumerate(result["sections"].items()):
        with sec_cols[i]:
            label = key.replace("_", " ").title()
            icon = icons.get(key, "•")
            cls = score_class(val["score"])
            color = {"score-high": "var(--success)", "score-mid": "var(--warn)", "score-low": "var(--danger)"}[cls]
            st.markdown(f"""
            <div class="stat-card" style="text-align:center">
              <div style="font-size:1.5rem">{icon}</div>
              <div style="font-family:'DM Serif Display',serif;font-size:2rem;color:{color}">{val['score']}</div>
              <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em">{label}</div>
              <div style="font-size:0.8rem;color:var(--muted);margin-top:.5rem">{val['feedback']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Strengths & Improvements ──
    st.markdown('<div class="section-title">Strengths & Improvements</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown("**✅ Strengths**")
        render_bullets(result["strengths"])
    with right:
        st.markdown("**⚠️ Areas to Improve**")
        render_bullets(result["improvements"])

    # ── Skills ──
    st.markdown('<div class="section-title">Skills Analysis</div>', unsafe_allow_html=True)
    sk1, sk2 = st.columns(2)
    with sk1:
        st.markdown("**Skills Found**")
        render_tags(result["skills_found"], "tag-strong")
    with sk2:
        st.markdown("**Skills to Add**")
        render_tags(result["skills_missing"], "tag-miss") if result["skills_missing"] else st.markdown("*No gaps detected*")

    # ── ATS Tips ──
    st.markdown('<div class="section-title">ATS Optimization Tips</div>', unsafe_allow_html=True)
    render_bullets(result["ats_tips"])

    # ── Action Items ──
    st.markdown('<div class="section-title">🚀 Action Items</div>', unsafe_allow_html=True)
    for i, item in enumerate(result["action_items"], 1):
        st.markdown(f"""
        <div class="stat-card" style="display:flex;gap:1rem;align-items:flex-start">
          <div style="background:var(--accent);color:white;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">{i}</div>
          <p style="margin:3px 0 0">{item}</p>
        </div>
        """, unsafe_allow_html=True)

elif not uploaded_file:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:var(--muted)">
      <div style="font-size:4rem;margin-bottom:1rem">📄</div>
      <p style="font-size:1.1rem">Upload your resume above to get started</p>
      <p style="font-size:0.85rem">Supports PDF and DOCX · Powered by Claude AI</p>
    </div>
    """, unsafe_allow_html=True)