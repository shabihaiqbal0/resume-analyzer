import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json, os, time, re, io
import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CareerIQ Pro — AI Resume Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# MASTER CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@300;400;500;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:       #060812;
  --surface:  #0d1022;
  --card:     #131629;
  --card2:    #181d35;
  --border:   #1f2545;
  --a1:       #6366f1;
  --a2:       #ec4899;
  --a3:       #06b6d4;
  --a4:       #f59e0b;
  --green:    #10b981;
  --red:      #ef4444;
  --text:     #e2e8ff;
  --muted:    #64748b;
  --r:        14px;
}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text);background:var(--bg);}
.stApp{background:var(--bg);}
#MainMenu,footer,header{visibility:hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}

/* ── Animated gradient hero ── */
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.hero{
  background:linear-gradient(-45deg,#0d0221,#1a0533,#0d1b4b,#051a2e,#130833);
  background-size:400% 400%;
  animation:gradShift 12s ease infinite;
  border-radius:20px;border:1px solid var(--border);
  padding:2.8rem 2rem;text-align:center;margin-bottom:1.5rem;
  position:relative;overflow:hidden;
}
.hero::after{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 20% 50%,rgba(99,102,241,.3) 0%,transparent 55%),
              radial-gradient(ellipse at 80% 50%,rgba(236,72,153,.2) 0%,transparent 55%);
}
.hero-title{
  font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
  background:linear-gradient(90deg,#a78bfa,#818cf8,#67e8f9,#f0abfc);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  position:relative;z-index:1;margin:0 0 .4rem;
}
.hero-sub{color:#94a3b8;font-size:.95rem;letter-spacing:.04em;position:relative;z-index:1;}
.badges{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center;margin-top:1.2rem;position:relative;z-index:1;}
.b{padding:.3rem .8rem;border-radius:20px;font-size:.75rem;font-weight:700;letter-spacing:.04em;}
.b1{background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.5);color:#a5b4fc;}
.b2{background:rgba(236,72,153,.2);border:1px solid rgba(236,72,153,.5);color:#f9a8d4;}
.b3{background:rgba(6,182,212,.2);border:1px solid rgba(6,182,212,.5);color:#67e8f9;}
.b4{background:rgba(245,158,11,.2);border:1px solid rgba(245,158,11,.5);color:#fde68a;}
.b5{background:rgba(16,185,129,.2);border:1px solid rgba(16,185,129,.5);color:#6ee7b7;}

/* ── Cards ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:1.5rem;margin-bottom:1rem;}
.card-h{font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:var(--text);margin-bottom:1rem;display:flex;align-items:center;gap:.5rem;}

/* ── Textarea & Input ── */
.stTextArea textarea,.stTextInput input{
  background:#1e2140!important;border:1px solid var(--a1)!important;border-radius:10px!important;
  color:#ffffff!important;font-family:'DM Sans',sans-serif!important;font-size:.95rem!important;
  line-height:1.8!important;caret-color:var(--a2)!important;
}
.stTextArea textarea::placeholder,.stTextInput input::placeholder{color:#6b7db3!important;font-style:italic!important;}
.stTextArea textarea:focus,.stTextInput input:focus{
  border-color:var(--a2)!important;box-shadow:0 0 0 3px rgba(236,72,153,.25)!important;
  background:#242850!important;color:#f0e6ff!important;
}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,var(--a1),var(--a2))!important;color:white!important;
  border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;
  font-weight:700!important;letter-spacing:.03em!important;
  box-shadow:0 4px 20px rgba(99,102,241,.4)!important;transition:all .3s!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(99,102,241,.6)!important;}

/* ── Progress ── */
.stProgress>div>div{background:linear-gradient(90deg,var(--a1),var(--a2))!important;border-radius:99px!important;}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:12px!important;padding:4px!important;gap:3px!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:9px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.82rem!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--a1),var(--a2))!important;color:white!important;}

/* ── Metrics ── */
[data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;font-weight:800!important;color:var(--a3)!important;}

/* ── File uploader ── */
[data-testid="stFileUploader"]{background:var(--card)!important;border:2px dashed var(--a1)!important;border-radius:var(--r)!important;}

/* ── Select ── */
.stSelectbox div[data-baseweb="select"]>div{background:var(--card)!important;border-color:var(--border)!important;color:var(--text)!important;}

/* ── JD highlights ── */
.jd-box{background:var(--card2);border:1px solid var(--border);border-radius:var(--r);padding:1.2rem;line-height:2;font-size:.9rem;}
.ty{background:rgba(99,102,241,.25);color:#a5b4fc;padding:1px 7px;border-radius:5px;font-weight:600;}
.tt{background:rgba(6,182,212,.25);color:#67e8f9;padding:1px 7px;border-radius:5px;font-weight:600;}
.ts{background:rgba(245,158,11,.25);color:#fde68a;padding:1px 7px;border-radius:5px;font-weight:600;}
.tm{background:rgba(239,68,68,.25);color:#fca5a5;padding:1px 7px;border-radius:5px;font-weight:600;}
.tn{background:rgba(16,185,129,.25);color:#6ee7b7;padding:1px 7px;border-radius:5px;font-weight:600;}

/* ── Skill bar ── */
.sb-wrap{margin-bottom:.65rem;}
.sb-lbl{display:flex;justify-content:space-between;font-size:.83rem;margin-bottom:.25rem;}
.sb{height:7px;border-radius:99px;background:var(--border);overflow:hidden;}
.sf{height:100%;border-radius:99px;}

/* ── Notifications ── */
.ok{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.4);border-radius:10px;padding:.8rem 1rem;color:#6ee7b7;font-size:.88rem;margin-bottom:.8rem;}
.warn{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.4);border-radius:10px;padding:.8rem 1rem;color:#fde68a;font-size:.88rem;margin-bottom:.8rem;}
.err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.4);border-radius:10px;padding:.8rem 1rem;color:#fca5a5;font-size:.88rem;margin-bottom:.8rem;}

/* ── Chat bubbles ── */
.chat-user{background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.3);border-radius:12px 12px 2px 12px;padding:.8rem 1rem;margin-bottom:.6rem;font-size:.9rem;}
.chat-ai{background:rgba(6,182,212,.1);border:1px solid rgba(6,182,212,.3);border-radius:12px 12px 12px 2px;padding:.8rem 1rem;margin-bottom:.6rem;font-size:.9rem;}
.chat-label{font-size:.72rem;font-weight:700;margin-bottom:.3rem;letter-spacing:.04em;}

/* ── IQ cards ── */
.iq{background:rgba(99,102,241,.07);border:1px solid rgba(99,102,241,.3);border-radius:10px;padding:.75rem 1rem;margin-bottom:.5rem;font-size:.88rem;}
.iq-n{color:var(--a1);font-weight:800;margin-right:.4rem;}

/* ── Msg bubble ── */
.mb{background:var(--card);border-left:3px solid var(--a1);border-radius:0 10px 10px 0;padding:.85rem 1rem;margin-bottom:.65rem;font-size:.87rem;}
.mb-meta{color:var(--muted);font-size:.73rem;margin-bottom:.25rem;}

/* ── Score ring colors ── */
.score-num{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;}
.score-lbl{font-size:.7rem;color:var(--muted);letter-spacing:.05em;}

/* ── Section title ── */
.sec-title{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;color:var(--text);margin:1.2rem 0 .8rem;}

/* ── Legend row ── */
.leg{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.8rem;font-size:.78rem;}

/* ── Admin ── */
.admin-hdr{background:linear-gradient(135deg,#1f0a3d,#0d1b4b);border:1px solid rgba(99,102,241,.4);border-radius:var(--r);padding:1rem 1.5rem;text-align:center;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key, val in {
    "activity_log": [],
    "user_messages": [],
    "analysis": None,
    "resume_text": "",
    "cover_letter": "",
    "linkedin_tips": "",
    "interview_chat": [],
    "rewritten_resume": "",
    "salary_data": None,
    "roadmap": "",
    "admin_unlocked": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def log_activity(action, details=""):
    entry = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": action, "details": details}
    st.session_state.activity_log.insert(0, entry)
    try:
        logs = []
        if os.path.exists("activity_log.json"):
            with open("activity_log.json") as f: logs = json.load(f)
        logs.insert(0, entry)
        with open("activity_log.json", "w") as f: json.dump(logs[:500], f, indent=2)
    except: pass

def load_log():
    try:
        if os.path.exists("activity_log.json"):
            with open("activity_log.json") as f: return json.load(f)
    except: pass
    return []

def send_email(owner, smtp_u, smtp_p, subject, html):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"], msg["From"], msg["To"] = subject, smtp_u, owner
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls(); s.login(smtp_u, smtp_p); s.sendmail(smtp_u, owner, msg.as_string())
        return True
    except Exception as e: return str(e)

def email_html(action, details):
    rows = "".join(f"<tr><td style='padding:6px 12px;color:#8890b5;font-size:13px;'>{k}</td><td style='padding:6px 12px;color:#e8eaf6;font-size:13px;'>{v}</td></tr>" for k,v in details.items())
    return f"""<div style="background:#060812;padding:30px;font-family:Arial,sans-serif;">
      <div style="max-width:600px;margin:0 auto;background:#0d1022;border-radius:14px;border:1px solid #1f2545;overflow:hidden;">
        <div style="background:linear-gradient(135deg,#1a0533,#0d1b4b);padding:24px;text-align:center;">
          <h1 style="color:#a5b4fc;font-size:22px;margin:0;">🧠 CareerIQ Pro</h1>
          <p style="color:#64748b;font-size:13px;margin:6px 0 0;">Activity Notification</p>
        </div>
        <div style="padding:24px;">
          <h2 style="color:#f59e0b;font-size:16px;margin:0 0 16px;">📢 {action}</h2>
          <table style="width:100%;border-collapse:collapse;background:#131629;border-radius:10px;overflow:hidden;">{rows}</table>
          <p style="color:#64748b;font-size:12px;margin:16px 0 0;text-align:center;">CareerIQ Pro · {datetime.now().strftime("%d %b %Y, %H:%M")}</p>
        </div>
      </div></div>"""

def extract_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except: return ""

TECH_KW = ["Python","JavaScript","TypeScript","React","Node","SQL","NoSQL","PostgreSQL","MongoDB","AWS","Azure","GCP","Docker","Kubernetes","CI/CD","Git","REST","API","ML","AI","LLM","GPT","LangChain","FastAPI","Django","Flask","TensorFlow","PyTorch","Pandas","NumPy","Spark","Kafka","Redis","GraphQL","Vue","Angular","Java","C++","C#","Go","Rust","Swift","Kotlin","Linux","Bash","Terraform","Airflow","dbt","Snowflake","Databricks","HuggingFace","OpenAI","RAG","Vector DB","Pinecone","ChromaDB","CrewAI","FAISS","Streamlit","LangGraph","AutoGen","n8n","Zapier","Power BI","Tableau","Excel","Figma","Notion"]
SOFT_KW  = ["communication","teamwork","leadership","collaboration","problem-solving","analytical","critical thinking","time management","adaptability","agile","scrum","kanban","mentoring","stakeholder"]
MUST_KW  = ["required","must","mandatory","minimum","necessary","essential","at least"]
NICE_KW  = ["preferred","nice to have","plus","bonus","advantage","beneficial","optional"]

def highlight_jd(text):
    if not text.strip():
        return "<span style='color:#64748b;font-style:italic;'>Paste job description — keywords will glow automatically…</span>"
    lines = text.split("\n")
    out = []
    for line in lines:
        line = re.sub(r'(\d+\+?\s*(?:years?|yrs?)\s*(?:of\s*experience)?)', r'<span class="ty">\1</span>', line, flags=re.IGNORECASE)
        for kw in TECH_KW:
            line = re.compile(r'\b('+re.escape(kw)+r')\b', re.IGNORECASE).sub(r'<span class="tt">\1</span>', line)
        for kw in SOFT_KW:
            line = re.compile(r'\b('+re.escape(kw)+r'(?:\s\w+)?)\b', re.IGNORECASE).sub(r'<span class="ts">\1</span>', line)
        for kw in MUST_KW:
            line = re.compile(r'\b('+re.escape(kw)+r')\b', re.IGNORECASE).sub(r'<span class="tm">\1</span>', line)
        for kw in NICE_KW:
            line = re.compile(r'\b('+re.escape(kw)+r')\b', re.IGNORECASE).sub(r'<span class="tn">\1</span>', line)
        out.append(line)
    return "<br>".join(out)

def groq_chat(api_key, messages, model="llama-3.3-70b-versatile", stream=False):
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=2000, stream=stream)
    if stream: return resp
    return resp.choices[0].message.content

def gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#e2e8ff", "size": 13, "family": "DM Sans"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1f2545", "tickfont": {"color": "#64748b"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#131629",
            "bordercolor": "#1f2545",
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,.1)"},
                {"range": [40, 70], "color": "rgba(245,158,11,.1)"},
                {"range": [70, 100],"color": "rgba(16,185,129,.1)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": value}
        },
        number={"font": {"color": color, "size": 36, "family": "Syne"}, "suffix": "%"}
    ))
    fig.update_layout(paper_bgcolor="#131629", height=200, margin=dict(t=30,b=10,l=20,r=20))
    return fig

def radar_chart(skills, values):
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=skills + [skills[0]],
        fill='toself',
        fillcolor='rgba(99,102,241,0.15)',
        line=dict(color='#6366f1', width=2),
        marker=dict(color='#ec4899', size=6),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#64748b", size=10), gridcolor="#1f2545"),
            angularaxis=dict(tickfont=dict(color="#e2e8ff", size=11), gridcolor="#1f2545"),
            bgcolor="#131629"
        ),
        paper_bgcolor="#131629", plot_bgcolor="#131629",
        height=320, margin=dict(t=20,b=20,l=40,r=40),
        showlegend=False
    )
    return fig

def bar_chart(labels, values, colors):
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v}%" for v in values], textposition='outside',
        textfont=dict(color="#e2e8ff", size=11)
    ))
    fig.update_layout(
        paper_bgcolor="#131629", plot_bgcolor="#131629",
        height=280, margin=dict(t=10,b=10,l=10,r=60),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0,115]),
        yaxis=dict(tickfont=dict(color="#e2e8ff", size=11), gridcolor="#1f2545"),
        bargap=0.3
    )
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:.5rem 0 1rem;'>
      <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;
                  background:linear-gradient(90deg,#a78bfa,#67e8f9);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        🧠 CareerIQ Pro
      </div>
      <div style='color:#64748b;font-size:.75rem;'>AI Resume Intelligence</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**⚙️ AI Settings**")
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_…")
    model_choice = st.selectbox("AI Model", ["llama-3.3-70b-versatile","llama-3.1-70b-versatile","mixtral-8x7b-32768","gemma2-9b-it"])

    st.markdown("---")
    st.markdown("**📧 Email Notifications**")
    owner_email = st.text_input("Your Email", placeholder="you@gmail.com")
    smtp_user   = st.text_input("Gmail Sender", placeholder="sender@gmail.com")
    smtp_pass   = st.text_input("App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")
    notif_on    = st.toggle("Enable Email Alerts", value=False)

    st.markdown("---")
    st.markdown("**🔐 Admin**")
    admin_pw = st.text_input("Admin Password", type="password")
    if st.button("🔓 Unlock Admin"):
        if admin_pw == "admin123":
            st.session_state.admin_unlocked = True
            st.success("✅ Unlocked!")
        else:
            st.error("❌ Wrong password")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:.73rem;color:#64748b;line-height:1.9;text-align:center;'>
    <b style='color:#a5b4fc;'>8 AI Features</b><br>
    ✅ Real Groq AI Analysis<br>
    ✅ ATS + Skills Scoring<br>
    ✅ Resume Rewriter<br>
    ✅ Cover Letter AI<br>
    ✅ Interview Simulator<br>
    ✅ LinkedIn Optimizer<br>
    ✅ Salary Estimator<br>
    ✅ Career Roadmap AI<br>
    ✅ Email Notifications<br>
    ✅ Admin Dashboard
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🧠 CareerIQ Pro</div>
  <div class="hero-sub">The World's Most Advanced AI Resume Intelligence Platform</div>
  <div class="badges">
    <span class="b b1">⚡ Real Groq AI</span>
    <span class="b b2">🎯 ATS Optimizer</span>
    <span class="b b3">📊 Smart Scoring</span>
    <span class="b b4">💡 Interview Coach</span>
    <span class="b b5">✍️ Resume Rewriter</span>
    <span class="b b1">📝 Cover Letter AI</span>
    <span class="b b2">💼 LinkedIn Pro</span>
    <span class="b b3">💰 Salary Insights</span>
    <span class="b b4">🗺️ Career Roadmap</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UPLOAD ZONE (always visible top)
# ─────────────────────────────────────────────
u1, u2 = st.columns([1,1], gap="large")
with u1:
    st.markdown('<div class="card"><div class="card-h">📄 Upload Resume (PDF)</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("Drop PDF here", type=["pdf"], label_visibility="collapsed")
    if resume_file:
        txt = extract_pdf(resume_file)
        st.session_state.resume_text = txt
        st.markdown(f'<div class="ok">✅ <b>{resume_file.name}</b> · {resume_file.size//1024} KB · {len(txt.split())} words extracted</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with u2:
    st.markdown('<div class="card"><div class="card-h">📋 Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area("Paste JD", placeholder="Paste the full job description here…", height=130, label_visibility="collapsed", key="jd_main")
    st.markdown('</div>', unsafe_allow_html=True)

# JD Highlight preview
if jd:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="leg">
      <span class="ty">Years</span><span class="tt">Tech Skills</span>
      <span class="ts">Soft Skills</span><span class="tm">Required</span><span class="tn">Nice-to-Have</span>
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="jd-box">{highlight_jd(jd)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────
t1,t2,t3,t4,t5,t6,t7,t8,t9 = st.tabs([
    "🎯 ATS Analysis",
    "✍️ Resume Rewriter",
    "📝 Cover Letter",
    "🎤 Interview Sim",
    "💼 LinkedIn Pro",
    "💰 Salary Intel",
    "🗺️ Career Roadmap",
    "💬 Messages",
    "👑 Admin"
])

# ══════════════════════════════════════════════
# TAB 1 — ATS ANALYSIS
# ══════════════════════════════════════════════
with t1:
    st.markdown('<div class="sec-title">🎯 Full AI Resume Analysis</div>', unsafe_allow_html=True)

    if st.button("🚀 Run Full AI Analysis", use_container_width=True, key="analyze_btn"):
        if not st.session_state.resume_text:
            st.markdown('<div class="err">❌ Please upload a resume PDF first.</div>', unsafe_allow_html=True)
        elif not groq_key:
            st.markdown('<div class="warn">⚠️ Enter your Groq API Key in the sidebar.</div>', unsafe_allow_html=True)
        else:
            log_activity("Resume Analysis", f"File: {resume_file.name if resume_file else 'N/A'}")
            if notif_on and owner_email and smtp_user and smtp_pass:
                send_email(owner_email, smtp_user, smtp_pass,
                    "🚀 New Resume Analysis — CareerIQ Pro",
                    email_html("New Resume Analysis", {
                        "File": resume_file.name if resume_file else "N/A",
                        "JD Preview": jd[:200]+"…" if jd else "None",
                        "Time": datetime.now().strftime("%d %b %Y, %H:%M")
                    }))

            with st.spinner("🤖 AI agents analyzing your resume…"):
                pb = st.progress(0)
                steps = ["📥 Reading resume…","🔍 Extracting skills…","📊 ATS check…","🤖 Scoring quality…","🎯 JD matching…","💡 Building recommendations…","✅ Finalizing…"]
                ph = st.empty()
                for i,s in enumerate(steps):
                    ph.markdown(f"<div style='color:#a5b4fc;font-size:.88rem;'>{s}</div>",unsafe_allow_html=True)
                    pb.progress((i+1)/len(steps)); time.sleep(0.3)
                ph.empty(); pb.empty()

                prompt = f"""You are an expert ATS resume analyzer and career coach. Analyze this resume against the job description.

RESUME:
{st.session_state.resume_text[:3000]}

JOB DESCRIPTION:
{jd[:1500] if jd else "Not provided"}

Return a JSON object with EXACTLY this structure (no markdown, pure JSON):
{{
  "ats_score": <number 0-100>,
  "jd_match": <number 0-100>,
  "quality_score": <number 0-100>,
  "keyword_score": <number 0-100>,
  "format_score": <number 0-100>,
  "matched_skills": [<list of 6-8 skills found>],
  "missing_skills": [<list of 4-6 important missing keywords>],
  "strengths": [<3 specific strengths>],
  "weaknesses": [<3 specific weaknesses>],
  "recommendations": [<5 specific actionable improvements>],
  "interview_questions": [<5 likely interview questions>],
  "skill_ratings": {{"Python": 85, "Communication": 70, "Leadership": 60, "Technical": 80, "Domain Knowledge": 75}},
  "summary": "<2 sentence professional assessment>"
}}"""
                try:
                    raw = groq_chat(groq_key, [{"role":"user","content":prompt}], model_choice)
                    raw = raw.strip().replace("```json","").replace("```","").strip()
                    result = json.loads(raw)
                    st.session_state.analysis = result
                except Exception as e:
                    # fallback mock data
                    st.session_state.analysis = {
                        "ats_score":78,"jd_match":71,"quality_score":82,"keyword_score":74,"format_score":85,
                        "matched_skills":["Python","SQL","Machine Learning","API Development","Docker","Git","Data Analysis"],
                        "missing_skills":["Kubernetes","Terraform","dbt","Snowflake","LangChain"],
                        "strengths":["Strong technical Python background","Good project portfolio","Clear work history"],
                        "weaknesses":["Missing cloud certifications","No quantified achievements","Weak summary section"],
                        "recommendations":[
                            "Add metrics: 'Improved model accuracy by 23%' instead of generic descriptions",
                            "Include missing keywords: Kubernetes, Terraform, Snowflake for better ATS matching",
                            "Rewrite summary to highlight LLM/AI expertise specifically",
                            "Add GitHub links to showcase actual code quality",
                            "Get AWS/GCP certification — listed as preferred in JD"
                        ],
                        "interview_questions":[
                            "Describe your most complex ML pipeline in production.",
                            "How do you handle model drift and retraining strategies?",
                            "Walk me through a challenging API performance problem you solved.",
                            "What's your experience with LLM fine-tuning vs. prompt engineering?",
                            "How do you ensure data quality in your pipelines?"
                        ],
                        "skill_ratings":{"Python":85,"Communication":68,"Leadership":55,"Technical":80,"Domain Knowledge":72},
                        "summary": f"AI analysis encountered an issue ({str(e)[:60]}). Showing sample data. Please check your Groq API key."
                    }

    r = st.session_state.analysis
    if r:
        # Scores row
        st.markdown('<div class="sec-title">📊 Score Dashboard</div>', unsafe_allow_html=True)
        g1,g2,g3,g4,g5 = st.columns(5)
        scores = [
            (g1,"ATS Score",r["ats_score"],"#6366f1"),
            (g2,"JD Match",r["jd_match"],"#ec4899"),
            (g3,"Quality",r["quality_score"],"#06b6d4"),
            (g4,"Keywords",r["keyword_score"],"#f59e0b"),
            (g5,"Format",r["format_score"],"#10b981"),
        ]
        for col,title,val,color in scores:
            with col:
                fig = gauge_chart(val, title, color)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        # Summary
        if r.get("summary"):
            st.markdown(f'<div class="ok">🧠 <b>AI Assessment:</b> {r["summary"]}</div>', unsafe_allow_html=True)

        # Charts + details
        c1,c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="card"><div class="card-h">🕸️ Skills Radar</div>', unsafe_allow_html=True)
            skills_r = list(r["skill_ratings"].keys())
            vals_r   = list(r["skill_ratings"].values())
            st.plotly_chart(radar_chart(skills_r, vals_r), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-h">✅ Matched Skills</div>', unsafe_allow_html=True)
            pills = " ".join(f'<span class="tt" style="display:inline-block;margin:3px;">{s}</span>' for s in r["matched_skills"])
            st.markdown(pills, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card"><div class="card-h">📈 Strength Breakdown</div>', unsafe_allow_html=True)
            sk = list(r["skill_ratings"].keys())
            sv = list(r["skill_ratings"].values())
            colors = ["#6366f1" if v>=80 else "#06b6d4" if v>=65 else "#f59e0b" for v in sv]
            st.plotly_chart(bar_chart(sk,sv,colors), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-h">⚠️ Missing Keywords</div>', unsafe_allow_html=True)
            pills2 = " ".join(f'<span class="tm" style="display:inline-block;margin:3px;">{s}</span>' for s in r["missing_skills"])
            st.markdown(pills2, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Recommendations + Interview Qs
        r1,r2 = st.columns(2, gap="large")
        with r1:
            st.markdown('<div class="card"><div class="card-h">🔧 AI Recommendations</div>', unsafe_allow_html=True)
            for i,rec in enumerate(r["recommendations"],1):
                st.markdown(f'<div class="iq"><span class="iq-n">{i}.</span>{rec}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with r2:
            st.markdown('<div class="card"><div class="card-h">💡 Predicted Interview Questions</div>', unsafe_allow_html=True)
            for i,q in enumerate(r["interview_questions"],1):
                st.markdown(f'<div class="iq"><span class="iq-n">Q{i}.</span>{q}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Strengths / Weaknesses
        sw1,sw2 = st.columns(2, gap="large")
        with sw1:
            st.markdown('<div class="card"><div class="card-h">💪 Key Strengths</div>', unsafe_allow_html=True)
            for s in r["strengths"]:
                st.markdown(f'<div style="color:#6ee7b7;font-size:.9rem;padding:.3rem 0;">✅ {s}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sw2:
            st.markdown('<div class="card"><div class="card-h">🚧 Areas to Improve</div>', unsafe_allow_html=True)
            for w in r["weaknesses"]:
                st.markdown(f'<div style="color:#fca5a5;font-size:.9rem;padding:.3rem 0;">⚠️ {w}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — RESUME REWRITER
# ══════════════════════════════════════════════
with t2:
    st.markdown('<div class="sec-title">✍️ AI Resume Rewriter</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:.9rem;margin-bottom:1rem;">Paste any weak section — AI rewrites it to be powerful, ATS-friendly, and impactful.</div>', unsafe_allow_html=True)

    rw1,rw2 = st.columns(2, gap="large")
    with rw1:
        st.markdown('<div class="card"><div class="card-h">📥 Original Text</div>', unsafe_allow_html=True)
        original_section = st.text_area("Paste weak section here", placeholder="e.g. 'Worked on machine learning projects and helped team with various tasks…'", height=200, label_visibility="collapsed")
        section_type = st.selectbox("Section Type", ["Work Experience","Summary/Objective","Skills Section","Project Description","Education","Achievements"])
        tone = st.selectbox("Tone", ["Professional & Powerful","Technical & Precise","Executive-Level","Creative & Dynamic"])
        if st.button("✨ Rewrite with AI", use_container_width=True, key="rewrite_btn"):
            if not original_section:
                st.markdown('<div class="err">❌ Please paste text to rewrite.</div>', unsafe_allow_html=True)
            elif not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key in sidebar.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("✍️ AI rewriting…"):
                    prompt = f"""You are an elite resume writer. Rewrite this {section_type} section.
Tone: {tone}
JD context: {jd[:500] if jd else "General tech role"}

ORIGINAL:
{original_section}

Rules: Use strong action verbs. Add metrics where possible. Use ATS keywords. Make it impactful and quantified. Return ONLY the rewritten text, no explanations."""
                    try:
                        st.session_state.rewritten_resume = groq_chat(groq_key,[{"role":"user","content":prompt}],model_choice)
                        log_activity("Resume Section Rewritten", section_type)
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ Error: {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rw2:
        st.markdown('<div class="card"><div class="card-h">✨ AI Rewritten Version</div>', unsafe_allow_html=True)
        if st.session_state.rewritten_resume:
            st.markdown(f'<div style="background:#1e2140;border:1px solid #6366f1;border-radius:10px;padding:1rem;color:#e2e8ff;font-size:.9rem;line-height:1.8;white-space:pre-wrap;">{st.session_state.rewritten_resume}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Copy Rewritten Text", st.session_state.rewritten_resume, "rewritten_section.txt")
        else:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Rewritten text will appear here…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — COVER LETTER
# ══════════════════════════════════════════════
with t3:
    st.markdown('<div class="sec-title">📝 AI Cover Letter Generator</div>', unsafe_allow_html=True)
    cl1,cl2 = st.columns([1,2], gap="large")
    with cl1:
        st.markdown('<div class="card"><div class="card-h">⚙️ Settings</div>', unsafe_allow_html=True)
        company_name  = st.text_input("Company Name", placeholder="e.g. Google")
        job_title     = st.text_input("Job Title",    placeholder="e.g. Senior ML Engineer")
        your_name     = st.text_input("Your Name",    placeholder="e.g. Sarah Ahmed")
        cl_tone       = st.selectbox("Cover Letter Tone",["Professional","Enthusiastic","Executive","Creative"])
        cl_length     = st.selectbox("Length",["Short (3 paragraphs)","Standard (4 paragraphs)","Detailed (5 paragraphs)"])
        if st.button("📝 Generate Cover Letter", use_container_width=True):
            if not st.session_state.resume_text and not jd:
                st.markdown('<div class="warn">⚠️ Upload resume or paste JD first.</div>', unsafe_allow_html=True)
            elif not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("📝 Writing cover letter…"):
                    prompt = f"""Write a {cl_tone.lower()} cover letter for {your_name or 'the candidate'} applying to {job_title or 'this role'} at {company_name or 'this company'}.
Length: {cl_length}
Resume summary: {st.session_state.resume_text[:1500] if st.session_state.resume_text else "Experienced professional"}
Job description: {jd[:800] if jd else "Technical role"}
Write a compelling, personalized cover letter. No placeholder text. Make it sound genuinely human and motivated."""
                    try:
                        st.session_state.cover_letter = groq_chat(groq_key,[{"role":"user","content":prompt}],model_choice)
                        log_activity("Cover Letter Generated", f"{job_title} at {company_name}")
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cl2:
        st.markdown('<div class="card"><div class="card-h">📄 Your Cover Letter</div>', unsafe_allow_html=True)
        if st.session_state.cover_letter:
            st.markdown(f'<div style="background:#1e2140;border:1px solid #6366f1;border-radius:10px;padding:1.2rem;color:#e2e8ff;font-size:.9rem;line-height:1.9;white-space:pre-wrap;">{st.session_state.cover_letter}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download Cover Letter", st.session_state.cover_letter, f"cover_letter_{company_name or 'job'}.txt")
        else:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Your personalized cover letter will appear here…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — INTERVIEW SIMULATOR
# ══════════════════════════════════════════════
with t4:
    st.markdown('<div class="sec-title">🎤 AI Interview Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:.9rem;margin-bottom:1rem;">Practice with an AI interviewer that asks role-specific questions and gives real feedback.</div>', unsafe_allow_html=True)

    iv1,iv2 = st.columns([1,2], gap="large")
    with iv1:
        st.markdown('<div class="card"><div class="card-h">🎯 Interview Setup</div>', unsafe_allow_html=True)
        iv_role  = st.text_input("Role Applying For", placeholder="e.g. Data Scientist")
        iv_level = st.selectbox("Interview Level", ["Entry Level","Mid Level","Senior","Lead/Manager","Director"])
        iv_type  = st.selectbox("Interview Type", ["Technical","Behavioral","Mixed","HR Screening","Case Study"])
        if st.button("🎤 Start Interview", use_container_width=True):
            if not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key.</div>', unsafe_allow_html=True)
            else:
                st.session_state.interview_chat = []
                sys_msg = f"""You are a professional interviewer for a {iv_level} {iv_role or 'tech'} position. 
Interview type: {iv_type}. Resume context: {st.session_state.resume_text[:800] if st.session_state.resume_text else "N/A"}
Ask ONE question at a time. After user answers, give brief feedback (1-2 sentences), then ask next question. Keep it realistic and challenging."""
                st.session_state.interview_chat = [{"role":"system","content":sys_msg}]
                with st.spinner("Starting interview…"):
                    try:
                        q = groq_chat(groq_key, st.session_state.interview_chat + [{"role":"user","content":"Start the interview. Ask your first question."}], model_choice)
                        st.session_state.interview_chat.append({"role":"assistant","content":q})
                        log_activity("Interview Started", f"{iv_level} {iv_role} - {iv_type}")
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with iv2:
        st.markdown('<div class="card"><div class="card-h">💬 Interview Chat</div>', unsafe_allow_html=True)
        chat = st.session_state.interview_chat
        for msg in [m for m in chat if m["role"] != "system"]:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-ai"><div class="chat-label" style="color:#67e8f9;">🤖 AI INTERVIEWER</div>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user"><div class="chat-label" style="color:#a5b4fc;">👤 YOU</div>{msg["content"]}</div>', unsafe_allow_html=True)

        if chat and len([m for m in chat if m["role"]!="system"]) > 0:
            user_answer = st.text_area("Your Answer", placeholder="Type your answer here…", height=100, label_visibility="collapsed", key="iv_answer")
            if st.button("📨 Send Answer", use_container_width=True):
                if user_answer and groq_key:
                    st.session_state.interview_chat.append({"role":"user","content":user_answer})
                    with st.spinner("AI thinking…"):
                        try:
                            reply = groq_chat(groq_key, st.session_state.interview_chat, model_choice)
                            st.session_state.interview_chat.append({"role":"assistant","content":reply})
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        elif not chat:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Click "Start Interview" to begin your practice session…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — LINKEDIN OPTIMIZER
# ══════════════════════════════════════════════
with t5:
    st.markdown('<div class="sec-title">💼 LinkedIn Profile Optimizer</div>', unsafe_allow_html=True)
    li1,li2 = st.columns([1,1], gap="large")
    with li1:
        st.markdown('<div class="card"><div class="card-h">📥 Your LinkedIn Sections</div>', unsafe_allow_html=True)
        li_headline  = st.text_input("Current Headline", placeholder="e.g. Data Scientist | Python | ML")
        li_about     = st.text_area("About Section", placeholder="Paste your current LinkedIn About…", height=120, label_visibility="visible")
        li_target    = st.text_input("Target Role", placeholder="e.g. Senior AI Engineer at FAANG")
        if st.button("💼 Optimize My LinkedIn", use_container_width=True):
            if not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("💼 Optimizing LinkedIn profile…"):
                    prompt = f"""You are a LinkedIn expert and personal branding coach. Optimize this person's LinkedIn profile.
Target role: {li_target or 'Senior tech role'}
Current headline: {li_headline or 'Not provided'}
Current about: {li_about or 'Not provided'}
Resume context: {st.session_state.resume_text[:1000] if st.session_state.resume_text else "N/A"}
JD context: {jd[:500] if jd else "N/A"}

Provide:
1. **Optimized Headline** (120 chars max, keyword-rich)
2. **Optimized About Section** (2000 chars, storytelling approach, keywords)
3. **5 Skills to Add** (most searched by recruiters)
4. **3 Quick Profile Wins** (specific actions to boost visibility)
5. **LinkedIn SEO Keywords** to include

Make it authentic, compelling, and recruiter-magnet quality."""
                    try:
                        st.session_state.linkedin_tips = groq_chat(groq_key,[{"role":"user","content":prompt}],model_choice)
                        log_activity("LinkedIn Optimized", li_target or "General")
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with li2:
        st.markdown('<div class="card"><div class="card-h">✨ Optimized Profile</div>', unsafe_allow_html=True)
        if st.session_state.linkedin_tips:
            st.markdown(f'<div style="background:#1e2140;border:1px solid #6366f1;border-radius:10px;padding:1.2rem;color:#e2e8ff;font-size:.88rem;line-height:1.9;white-space:pre-wrap;">{st.session_state.linkedin_tips}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Optimized LinkedIn content will appear here…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 6 — SALARY ESTIMATOR
# ══════════════════════════════════════════════
with t6:
    st.markdown('<div class="sec-title">💰 AI Salary Intelligence</div>', unsafe_allow_html=True)
    sa1,sa2 = st.columns([1,1], gap="large")
    with sa1:
        st.markdown('<div class="card"><div class="card-h">📊 Your Profile</div>', unsafe_allow_html=True)
        sal_role     = st.text_input("Job Title", placeholder="e.g. Machine Learning Engineer")
        sal_exp      = st.selectbox("Years of Experience", ["0-1 years","2-3 years","4-5 years","6-8 years","9-12 years","13+ years"])
        sal_country  = st.text_input("Country/City", placeholder="e.g. USA, San Francisco")
        sal_industry = st.selectbox("Industry", ["Tech/Software","Finance/Fintech","Healthcare","E-commerce","Consulting","Startup","Government","Education"])
        if st.button("💰 Estimate Salary", use_container_width=True):
            if not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("💰 Analyzing market data…"):
                    prompt = f"""You are a compensation expert with deep knowledge of tech salaries globally.
Role: {sal_role or 'Software Engineer'}
Experience: {sal_exp}
Location: {sal_country or 'USA'}
Industry: {sal_industry}
Skills from resume: {", ".join(TECH_KW[:10]) if st.session_state.resume_text else "Python, SQL, ML"}

Return a detailed salary analysis with:
1. **Salary Range** (min, mid, max in USD/local currency)
2. **Total Compensation** (base + bonus + equity estimate)
3. **Market Percentile** (where this profile sits)
4. **Top Paying Companies** for this role
5. **Skills that increase salary** (3-4 specific ones)
6. **Negotiation Tips** (3 specific tactics)
7. **5-Year Earning Trajectory**

Be specific with numbers. Use current 2024-2025 market data."""
                    try:
                        salary_text = groq_chat(groq_key,[{"role":"user","content":prompt}],model_choice)
                        st.session_state.salary_data = salary_text
                        log_activity("Salary Estimated", f"{sal_role} - {sal_country}")
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with sa2:
        st.markdown('<div class="card"><div class="card-h">💎 Salary Intelligence Report</div>', unsafe_allow_html=True)
        if st.session_state.salary_data:
            st.markdown(f'<div style="background:#1e2140;border:1px solid #f59e0b;border-radius:10px;padding:1.2rem;color:#e2e8ff;font-size:.88rem;line-height:1.9;white-space:pre-wrap;">{st.session_state.salary_data}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Salary intelligence will appear here…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 7 — CAREER ROADMAP
# ══════════════════════════════════════════════
with t7:
    st.markdown('<div class="sec-title">🗺️ AI Career Roadmap Generator</div>', unsafe_allow_html=True)
    rm1,rm2 = st.columns([1,2], gap="large")
    with rm1:
        st.markdown('<div class="card"><div class="card-h">🎯 Your Goals</div>', unsafe_allow_html=True)
        rm_current = st.text_input("Current Role", placeholder="e.g. Junior Data Analyst")
        rm_goal    = st.text_input("Dream Role in 5 Years", placeholder="e.g. AI Research Scientist at OpenAI")
        rm_timeline= st.selectbox("Timeline", ["6 months","1 year","2 years","3 years","5 years"])
        rm_focus   = st.multiselect("Focus Areas", ["Technical Skills","Leadership","Certifications","Networking","Projects/Portfolio","Open Source","Research/Publications","Entrepreneurship"], default=["Technical Skills","Certifications"])
        if st.button("🗺️ Generate My Roadmap", use_container_width=True):
            if not groq_key:
                st.markdown('<div class="warn">⚠️ Add Groq API key.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("🗺️ Building your career roadmap…"):
                    prompt = f"""You are a world-class career strategist. Create a detailed career roadmap.
Current role: {rm_current or 'Early career professional'}
Goal: {rm_goal or 'Senior tech leadership role'}
Timeline: {rm_timeline}
Focus: {', '.join(rm_focus) if rm_focus else 'Technical growth'}
Resume context: {st.session_state.resume_text[:800] if st.session_state.resume_text else "N/A"}

Create a month-by-month or quarter-by-quarter roadmap with:
1. **Phase-by-phase milestones**
2. **Specific skills to learn** (with resources)
3. **Certifications to get** (with priority order)
4. **Projects to build** (portfolio items)
5. **Networking moves** (communities, events, people to connect with)
6. **Job titles progression** (stepping stones)
7. **30-60-90 day quick wins** to start immediately

Be extremely specific and actionable. No generic advice."""
                    try:
                        st.session_state.roadmap = groq_chat(groq_key,[{"role":"user","content":prompt}],model_choice)
                        log_activity("Career Roadmap Generated", f"{rm_current} → {rm_goal}")
                    except Exception as e:
                        st.markdown(f'<div class="err">❌ {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rm2:
        st.markdown('<div class="card"><div class="card-h">🗺️ Your Personalized Career Roadmap</div>', unsafe_allow_html=True)
        if st.session_state.roadmap:
            st.markdown(f'<div style="background:#1e2140;border:1px solid #10b981;border-radius:10px;padding:1.2rem;color:#e2e8ff;font-size:.88rem;line-height:1.9;white-space:pre-wrap;">{st.session_state.roadmap}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download Roadmap", st.session_state.roadmap, "career_roadmap.txt")
        else:
            st.markdown('<div style="color:#64748b;font-style:italic;font-size:.9rem;">Your personalized career roadmap will appear here…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 8 — MESSAGES
# ══════════════════════════════════════════════
with t8:
    st.markdown('<div class="sec-title">💬 Messages & Activity</div>', unsafe_allow_html=True)
    mc1,mc2 = st.columns(2, gap="large")

    with mc1:
        st.markdown('<div class="card"><div class="card-h">✉️ Send Message to Owner</div>', unsafe_allow_html=True)
        msg_name  = st.text_input("Your Name",  placeholder="e.g. Ali Hassan", key="msg_name")
        msg_email = st.text_input("Your Email", placeholder="ali@email.com",   key="msg_email")
        msg_text  = st.text_area("Message",     placeholder="Your question or feedback…", height=120, key="msg_text")
        if st.button("📨 Send Message", use_container_width=True, key="send_msg"):
            if msg_text.strip():
                entry = {"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"name":msg_name or "Anonymous","email":msg_email,"message":msg_text}
                st.session_state.user_messages.insert(0, entry)
                log_activity("New Message", f"From: {msg_name} | {msg_email} | {msg_text[:100]}")
                if notif_on and owner_email and smtp_user and smtp_pass:
                    r = send_email(owner_email, smtp_user, smtp_pass,
                        f"📩 New Message from {msg_name or 'Anonymous'}",
                        email_html("New User Message", {"From":msg_name,"Email":msg_email,"Message":msg_text,"Time":datetime.now().strftime("%d %b %Y, %H:%M")}))
                    if r is True: st.markdown('<div class="ok">✅ Sent! Owner notified by email.</div>', unsafe_allow_html=True)
                    else: st.markdown(f'<div class="warn">⚠️ Saved but email failed: {r}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="ok">✅ Message saved!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-h">📋 Received Messages</div>', unsafe_allow_html=True)
        msgs = st.session_state.user_messages
        if not msgs:
            st.markdown('<div style="color:#64748b;font-size:.88rem;">No messages yet.</div>', unsafe_allow_html=True)
        for m in msgs:
            st.markdown(f'<div class="mb"><div class="mb-meta">👤 <b>{m["name"]}</b> {("· "+m["email"]) if m["email"] else ""} · {m["time"]}</div>{m["message"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with mc2:
        st.markdown('<div class="card"><div class="card-h">📊 Live Activity Feed</div>', unsafe_allow_html=True)
        all_logs = st.session_state.activity_log or load_log()
        if not all_logs:
            st.markdown('<div style="color:#64748b;font-size:.88rem;">No activity yet.</div>', unsafe_allow_html=True)
        for e in all_logs[:25]:
            ac = {"Resume Analysis":"#6366f1","Cover Letter Generated":"#ec4899","Interview Started":"#06b6d4","Salary Estimated":"#f59e0b","New Message":"#10b981","LinkedIn Optimized":"#a78bfa","Career Roadmap Generated":"#67e8f9"}.get(e["action"],"#64748b")
            st.markdown(f'<div class="mb" style="border-color:{ac};"><div class="mb-meta">🕐 {e["time"]} · <span style="color:{ac};font-weight:700;">{e["action"]}</span></div><div style="font-size:.82rem;color:#94a3b8;">{e["details"][:150]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 9 — ADMIN
# ══════════════════════════════════════════════
with t9:
    if st.session_state.admin_unlocked:
        st.markdown('<div class="admin-hdr"><div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#f59e0b;">👑 Admin Dashboard</div></div>', unsafe_allow_html=True)
        all_logs = load_log()
        a1,a2,a3,a4 = st.columns(4)
        a1.metric("📊 Analyses",    sum(1 for e in all_logs if "Analysis" in e.get("action","")))
        a2.metric("📝 Cover Letters",sum(1 for e in all_logs if "Cover" in e.get("action","")))
        a3.metric("💬 Messages",    sum(1 for e in all_logs if "Message" in e.get("action","")))
        a4.metric("📋 Total Events", len(all_logs))

        st.markdown("---")
        st.markdown('<div class="card"><div class="card-h">📋 Full Event Log</div>', unsafe_allow_html=True)
        for e in all_logs:
            st.markdown(f'<div class="mb"><div class="mb-meta">🕐 {e["time"]} · <b>{e["action"]}</b></div><div style="font-size:.82rem;">{e["details"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear All Logs"):
            st.session_state.activity_log = []
            try:
                with open("activity_log.json","w") as f: json.dump([],f)
            except: pass
            st.rerun()
    else:
        st.markdown('<div style="text-align:center;padding:3rem;"><div style="font-size:3rem;">🔐</div><div style="font-family:Syne,sans-serif;font-size:1.1rem;color:#e2e8ff;margin:.8rem 0 .4rem;">Admin Panel Locked</div><div style="color:#64748b;font-size:.9rem;">Enter password in sidebar and click Unlock Admin</div></div>', unsafe_allow_html=True)