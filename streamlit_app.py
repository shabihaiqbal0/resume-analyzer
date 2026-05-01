"""
╔══════════════════════════════════════════════════════════╗
║         AI RESUME ANALYZER — Streamlit App               ║
║         LangChain • RAG • CrewAI • Ollama (FREE)         ║
╠══════════════════════════════════════════════════════════╣
║  HOW TO RUN:                                             ║
║  1. pip install streamlit langchain langchain-community  ║
║              langchain-ollama crewai chromadb pypdf      ║
║  2. Make sure Ollama is running: ollama serve            ║
║  3. Pull model: ollama pull llama3                       ║
║  4. streamlit run streamlit_app.py                       ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import time
import tempfile
import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Main title */
.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #f8f9fa, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
}

.sub-title {
    text-align: center;
    color: #a0aec0;
    font-size: 1rem;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

/* Section headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid rgba(167,139,250,0.3);
    padding-bottom: 0.4rem;
}

/* Score badge */
.score-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Status boxes */
.status-running {
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.4);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #93c5fd;
    font-size: 0.9rem;
    margin: 0.4rem 0;
}
.status-done {
    background: rgba(52,211,153,0.15);
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #6ee7b7;
    font-size: 0.9rem;
    margin: 0.4rem 0;
}
.status-error {
    background: rgba(248,113,113,0.15);
    border: 1px solid rgba(248,113,113,0.4);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #fca5a5;
    font-size: 0.9rem;
    margin: 0.4rem 0;
}

/* Metric boxes */
.metric-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-label {
    color: #718096;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.metric-value {
    color: #e2e8f0;
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.95) !important;
    border-right: 1px solid rgba(167,139,250,0.2);
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(167,139,250,0.4) !important;
    border-radius: 12px !important;
}

/* Text area */
textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Radio buttons */
.stRadio label { color: #cbd5e0 !important; }

/* All text color */
p, li, label, .stMarkdown { color: #cbd5e0 !important; }
h1, h2, h3 { color: #e2e8f0 !important; }

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
    color: #cbd5e0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  IMPORTS (lazy — only after page config)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_libs():
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from crewai import Agent, Task, Crew
    return PyPDFLoader, RecursiveCharacterTextSplitter, Chroma, Agent, Task, Crew

def get_llm_and_embeddings(provider, model_name, api_key=""):
    if provider == "Ollama (Free)":
        from langchain_ollama import ChatOllama
        from langchain_community.embeddings import OllamaEmbeddings
        return ChatOllama(model=model_name), OllamaEmbeddings(model=model_name)
    elif provider == "OpenAI":
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        os.environ["OPENAI_API_KEY"] = api_key
        return ChatOpenAI(model=model_name), OpenAIEmbeddings()
    elif provider == "Groq (Free tier)":
        from langchain_groq import ChatGroq
        from langchain_community.embeddings import OllamaEmbeddings
        os.environ["GROQ_API_KEY"] = api_key
        return ChatGroq(model=model_name), OllamaEmbeddings(model="llama3")


# ══════════════════════════════════════════════════════════════════════════════
#  CORE PIPELINE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def setup_resume_rag(pdf_path, embeddings):
    PyPDFLoader, RecursiveCharacterTextSplitter, Chroma, _, _, _ = load_libs()
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(chunks, embeddings)
    return vectorstore, len(chunks)

def get_resume_context(vectorstore, job_description):
    results = vectorstore.similarity_search(job_description, k=4)
    return "\n".join([r.page_content for r in results])

def run_crew(resume_context, job_description, llm):
    _, _, _, Agent, Task, Crew = load_libs()

    extractor = Agent(
        role="Resume Extractor",
        goal="Extract all skills, experience, education, achievements",
        backstory="You are an expert at reading resumes and pulling key info.",
        llm=llm, verbose=False
    )
    matcher = Agent(
        role="Job Matcher",
        goal="Compare resume details with job requirements and find gaps",
        backstory="You are a recruiter who knows what employers want.",
        llm=llm, verbose=False
    )
    coach = Agent(
        role="Career Coach",
        goal="Give a match score out of 100 and suggest improvements",
        backstory="You help candidates improve their resumes.",
        llm=llm, verbose=False
    )

    task1 = Task(
        description=f"Extract skills, experience, education from:\n{resume_context}",
        agent=extractor,
        expected_output="Bulleted list of skills, experience, education."
    )
    task2 = Task(
        description=f"Compare the extracted info with this job:\n{job_description}",
        agent=matcher,
        expected_output="Matches, missing skills, and gaps."
    )
    task3 = Task(
        description="Give a score out of 100 and 3-5 improvement tips.",
        agent=coach,
        expected_output="Match score and improvement suggestions."
    )

    crew = Crew(
        agents=[extractor, matcher, coach],
        tasks=[task1, task2, task3],
        verbose=False
    )
    return crew.kickoff()


def extract_score(result_text):
    """Try to pull score number from result text."""
    import re
    patterns = [r'(\d{1,3})\s*/\s*100', r'score[:\s]+(\d{1,3})', r'(\d{1,3})%']
    for pat in patterns:
        match = re.search(pat, str(result_text), re.IGNORECASE)
        if match:
            val = int(match.group(1))
            if 0 <= val <= 100:
                return val
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="section-header">⚙️  Configuration</div>', unsafe_allow_html=True)

    provider = st.radio(
        "AI Provider",
        ["Ollama (Free)", "OpenAI", "Groq (Free tier)"],
        index=0,
        help="Ollama is 100% free and runs locally."
    )

    if provider == "Ollama (Free)":
        model_name = st.selectbox("Model", ["llama3", "llama3.2", "mistral", "gemma2", "phi3"])
        api_key = ""
        st.markdown("""
        <div class="status-done">
        ✅ No API key needed!<br>
        Make sure Ollama is running:<br>
        <code>ollama serve</code><br>
        <code>ollama pull llama3</code>
        </div>
        """, unsafe_allow_html=True)

    elif provider == "OpenAI":
        model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"])
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    elif provider == "Groq (Free tier)":
        model_name = st.selectbox("Model", ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"])
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        st.markdown("""
        <div class="status-done">
        ✅ Free at console.groq.com
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📚  About</div>', unsafe_allow_html=True)
    st.markdown("""
    <small style='color:#718096'>
    Built with:<br>
    • LangChain (PDF + RAG)<br>
    • ChromaDB (Vector DB)<br>
    • CrewAI (Multi-Agent)<br>
    • Streamlit (UI)<br><br>
    3 Agents: Extractor → Matcher → Coach
    </small>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="main-title">AI Resume Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">LangChain • RAG • CrewAI • Multi-Agent Analysis</p>', unsafe_allow_html=True)

# ── Two columns: Upload + Job Description ─────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="section-header">📄  Upload Resume (PDF)</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your resume PDF here",
        type=["pdf"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.markdown(f"""
        <div class="status-done">
        ✅ Loaded: <strong>{uploaded_file.name}</strong> ({round(uploaded_file.size/1024,1)} KB)
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">💼  Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="""We are hiring a Python Developer with:
- 2+ years Python experience
- Knowledge of Django or Flask
- Experience with REST APIs
- Familiarity with SQL databases""",
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Analyze Button ─────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button("🚀  ANALYZE RESUME", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if analyze_clicked:

    # Validation
    if not uploaded_file:
        st.markdown('<div class="status-error">❌ Please upload a resume PDF first.</div>', unsafe_allow_html=True)
        st.stop()
    if not job_description.strip():
        st.markdown('<div class="status-error">❌ Please paste a job description.</div>', unsafe_allow_html=True)
        st.stop()
    if provider != "Ollama (Free)" and not api_key.strip():
        st.markdown('<div class="status-error">❌ Please enter your API key in the sidebar.</div>', unsafe_allow_html=True)
        st.stop()

    st.markdown("---")
    st.markdown('<div class="section-header">⚡  Pipeline Running</div>', unsafe_allow_html=True)

    # Progress bar
    progress = st.progress(0)
    status_area = st.empty()
    start_time = time.time()

    try:
        # Save PDF to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Step 1: Load PDF
        status_area.markdown('<div class="status-running">⏳ Step 1/4 — Loading PDF and splitting into chunks…</div>', unsafe_allow_html=True)
        progress.progress(10)
        llm, embeddings = get_llm_and_embeddings(provider, model_name, api_key)
        vectorstore, chunk_count = setup_resume_rag(tmp_path, embeddings)
        progress.progress(30)

        # Step 2: RAG retrieval
        status_area.markdown('<div class="status-running">⏳ Step 2/4 — Retrieving relevant resume sections (RAG)…</div>', unsafe_allow_html=True)
        resume_context = get_resume_context(vectorstore, job_description)
        progress.progress(45)

        # Step 3: Agent 1 — Extractor
        status_area.markdown('<div class="status-running">⏳ Step 3/4 — Agent 1 (Extractor) reading resume…</div>', unsafe_allow_html=True)
        progress.progress(55)

        # Step 4: Run full crew
        status_area.markdown('<div class="status-running">⏳ Step 4/4 — Agents 2 & 3 (Matcher + Career Coach) analyzing…</div>', unsafe_allow_html=True)
        result = run_crew(resume_context, job_description, llm)
        progress.progress(100)

        elapsed = round(time.time() - start_time, 1)
        status_area.markdown(f'<div class="status-done">✅ Analysis complete in {elapsed}s</div>', unsafe_allow_html=True)

        # Clean up temp file
        os.unlink(tmp_path)

        # ── RESULTS ────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊  Analysis Results</div>', unsafe_allow_html=True)

        # Metrics row
        score_val = extract_score(str(result))
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Match Score</div>
                <div class="metric-value" style="color:#a78bfa">{score_val if score_val else "—"}/100</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">PDF Chunks</div>
                <div class="metric-value">{chunk_count}</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Runtime</div>
                <div class="metric-value">{elapsed}s</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Agents Used</div>
                <div class="metric-value">3</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Score progress bar
        if score_val:
            color = "#34d399" if score_val >= 70 else "#fbbf24" if score_val >= 50 else "#f87171"
            st.markdown(f"""
            <div style="margin-bottom:1.5rem">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
                    <span style="color:#a0aec0;font-size:0.85rem">Resume Match</span>
                    <span style="color:{color};font-family:'Space Mono',monospace;font-weight:700">{score_val}/100</span>
                </div>
                <div style="background:rgba(255,255,255,0.08);border-radius:999px;height:10px">
                    <div style="width:{score_val}%;background:linear-gradient(90deg,#7c3aed,{color});height:10px;border-radius:999px;transition:width 1s ease"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Full report
        with st.expander("📋  Full Report (click to expand)", expanded=True):
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1.5rem;
                        font-family:'DM Sans',sans-serif;color:#e2e8f0;
                        border:1px solid rgba(255,255,255,0.08);white-space:pre-wrap;line-height:1.8">
{str(result)}
            </div>
            """, unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇️  Download Report as .txt",
            data=str(result),
            file_name="resume_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        # Viva Questions
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🎓  Viva / Review Questions (Section 9)"):
            questions = [
                "1. What is the difference between LangChain and CrewAI?",
                "2. Why do we split the PDF into chunks before storing in the vector database?",
                "3. What is an embedding, and why is it needed for RAG?",
                "4. What would happen if we set chunk_size too small or too large?",
                "5. How does the Matcher agent use the output of the Extractor agent?",
                "6. Name two advantages of using multiple agents instead of a single LLM call.",
                "7. How could you extend this project to analyze multiple resumes at once?",
                "8. What is the role of 'backstory' in a CrewAI Agent?",
            ]
            for q in questions:
                st.markdown(f"**{q}**")
                st.text_input("Your answer:", key=q, label_visibility="collapsed", placeholder="Type your answer here…")
                st.markdown("")

    except Exception as e:
        progress.progress(0)
        st.markdown(f"""
        <div class="status-error">
        ❌ Error: {str(e)}<br><br>
        <strong>Common fixes:</strong><br>
        • Ollama not running → run: <code>ollama serve</code><br>
        • Model not downloaded → run: <code>ollama pull llama3</code><br>
        • Wrong API key → check sidebar<br>
        • Missing package → <code>pip install langchain-ollama</code>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#4a5568;font-size:0.8rem;border-top:1px solid rgba(255,255,255,0.06);padding-top:1.5rem">
    AI Resume Analyzer &nbsp;•&nbsp; LangChain + RAG + CrewAI &nbsp;•&nbsp;
    Applied AI / Generative AI Course
</div>
""", unsafe_allow_html=True)
