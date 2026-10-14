import os
import sys
import io
import threading
import contextlib
from datetime import datetime
from pathlib import Path

# Force UTF-8 environment and encoding globally on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import streamlit as st
from dotenv import load_dotenv

try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
except Exception:
    add_script_run_ctx = None
    get_script_run_ctx = None

# Ensure 'src' is accessible in sys.path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv()

# Check Streamlit Cloud Secrets if available
try:
    if hasattr(st, "secrets"):
        for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]:
            if k in st.secrets and st.secrets[k]:
                os.environ[k] = str(st.secrets[k])
except Exception:
    pass

if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from researcher.crew import Researcher
from researcher.tools.export_utils import export_report
from researcher.tools.knowledge_utils import load_knowledge_documents, save_uploaded_knowledge_file

# Page Configuration
st.set_page_config(
    page_title="Researcher with CrewAI - Multi-Agent Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .step-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.4rem;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .step-card:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
    }
    .step-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-blue { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-emerald { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
    .step-title {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .step-agent {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .step-desc {
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.85rem;
    }
    .step-output {
        background: rgba(15, 23, 42, 0.6);
        border-left: 3px solid #38bdf8;
        padding: 0.4rem 0.7rem;
        font-size: 0.8rem;
        color: #e2e8f0;
        border-radius: 0 4px 4px 0;
    }
    .metric-badge {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-val { font-size: 1.25rem; font-weight: 800; color: #38bdf8; }
    .metric-lbl { font-size: 0.8rem; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)


class LiveOutputRedirector:
    """Redirects stdout and stderr to a real-time Streamlit log display safely across worker threads."""
    def __init__(self, code_placeholder):
        self.code_placeholder = code_placeholder
        self.lines = []
        self._stdout = sys.stdout
        self.encoding = "utf-8"
        self.errors = "replace"
        self.mode = "w"
        self._lock = threading.Lock()
        try:
            self.ctx = get_script_run_ctx() if get_script_run_ctx else None
        except Exception:
            self.ctx = None

    def write(self, text):
        if not text:
            return

        # 1. Safely mirror to system console without charmap / cp1252 crash
        try:
            self._stdout.write(text)
        except UnicodeEncodeError:
            try:
                enc = getattr(self._stdout, "encoding", "utf-8") or "utf-8"
                safe_text = text.encode(enc, errors="replace").decode(enc)
                self._stdout.write(safe_text)
            except Exception:
                pass
        except Exception:
            pass

        # 2. Safely capture text for Streamlit UI
        if text.strip():
            with self._lock:
                self.lines.append(text)
                if len(self.lines) > 200:
                    self.lines = self.lines[-100:]
                recent = "".join(self.lines[-35:])

            # 3. Safely update Streamlit UI, handling background threads
            try:
                if self.ctx and add_script_run_ctx and get_script_run_ctx and get_script_run_ctx() is None:
                    try:
                        add_script_run_ctx(threading.current_thread(), self.ctx)
                    except Exception:
                        pass
                self.code_placeholder.code(recent, language="bash")
            except Exception:
                # Never let a UI streaming failure crash the agent / CrewAI pipeline!
                pass

    def flush(self):
        try:
            self._stdout.flush()
        except Exception:
            pass

    def isatty(self):
        return False


def answer_report_query(question: str, report_text: str) -> str:
    """Answers follow-up questions grounded strictly on the research report."""
    prompt = f"""You are an elite research intelligence analyst.
Answer the user's inquiry accurately and concisely, drawing primarily from the provided research report below.
If details are not in the report, state that clearly and offer a reasonable analytical perspective.

RESEARCH REPORT:
{report_text[:14000]}

USER QUESTION:
{question}
"""
    # 1. Try LiteLLM
    try:
        import litellm
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            response = litellm.completion(
                model="gemini/gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                api_key=api_key,
                temperature=0.3
            )
            return response.choices[0].message.content
        elif os.getenv("OPENROUTER_API_KEY"):
            response = litellm.completion(
                model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("OPENROUTER_API_KEY"),
                temperature=0.3
            )
            return response.choices[0].message.content
    except Exception as e:
        pass

    # 2. Try Google GenAI SDK fallback
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as err:
        return f"Unable to process Q&A at this time: {str(err)}"


# ==============================================================
# SIDEBAR CONFIGURATION
# ==============================================================
with st.sidebar:
    st.title("⚙️ Controls & Status")

    # Check session state for persistent API key input across reruns
    if "custom_api_key" in st.session_state and st.session_state["custom_api_key"]:
        os.environ["GEMINI_API_KEY"] = st.session_state["custom_api_key"].strip()
        os.environ["GOOGLE_API_KEY"] = st.session_state["custom_api_key"].strip()

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if gemini_key:
        st.success("✅ Gemini 2.5 Flash Active")
    elif openrouter_key:
        st.success("✅ OpenRouter API Key Active")
    else:
        st.warning("⚠️ No API Key in Environment/Secrets")
        custom_key = st.text_input(
            "Enter Gemini API Key:",
            type="password",
            key="custom_api_key",
            help="Get a free API key at https://aistudio.google.com"
        )
        if custom_key:
            os.environ["GEMINI_API_KEY"] = custom_key.strip()
            os.environ["GOOGLE_API_KEY"] = custom_key.strip()
            st.success("✅ API Key active for this session!")

    st.markdown("---")
    st.subheader("🎛️ Research Preferences")
    research_depth = st.selectbox(
        "Research Depth:",
        options=["Comprehensive Deep Dive", "Quick Executive Brief", "Technical Whitepaper"],
        index=0
    )
    research_tone = st.selectbox(
        "Analytical Tone:",
        options=["Professional & Analytical", "Executive C-Level Brief", "Academic & Scholarly", "Investigative & Critical"],
        index=0
    )

    st.markdown("---")
    st.subheader("📁 Knowledge Base (RAG)")
    uploaded_files = st.file_uploader(
        "Upload reference documents (.pdf, .txt, .md):",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for f in uploaded_files:
            save_path = save_uploaded_knowledge_file(f, target_dir=str(BASE_DIR / "knowledge"))
            st.caption(f"Ingested: `{f.name}`")
        st.success(f"Ingested {len(uploaded_files)} file(s) into knowledge base!")

    # Show existing knowledge files
    knowledge_dir = BASE_DIR / "knowledge"
    if knowledge_dir.exists():
        k_files = [p.name for p in knowledge_dir.glob("*") if p.suffix.lower() in [".pdf", ".txt", ".md"]]
        if k_files:
            with st.expander(f"📚 Active Documents ({len(k_files)})"):
                for kf in k_files:
                    st.text(f"• {kf}")

    st.markdown("---")
    st.subheader("📚 Saved Reports History")
    reports_dir = BASE_DIR / "reports"
    if reports_dir.exists():
        md_files = sorted(list(reports_dir.glob("report_*.md")), reverse=True)
        if md_files:
            selected_file = st.selectbox(
                "Select a previous report:",
                options=md_files,
                format_func=lambda x: x.stem.replace("report_", "")
            )
            if selected_file:
                with open(selected_file, "r", encoding="utf-8") as f:
                    past_content = f.read()

                # Corresponding PDF and Audio if available
                base_stem = selected_file.stem
                pdf_match = reports_dir / f"{base_stem}.pdf"
                audio_match = reports_dir / f"{base_stem}.mp3"

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        label="📥 Download MD",
                        data=past_content,
                        file_name=selected_file.name,
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col_d2:
                    if pdf_match.exists():
                        with open(pdf_match, "rb") as pf:
                            st.download_button(
                                label="📥 Download PDF",
                                data=pf.read(),
                                file_name=pdf_match.name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                if audio_match.exists():
                    st.audio(str(audio_match))
        else:
            st.info("No past reports found yet.")


# ==============================================================
# MAIN PAGE LAYOUT
# ==============================================================
st.markdown('<div class="main-title">🔍 AI Research & Intelligence Crew</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Autonomous 3-Agent Collaborative Research Engine &bull; Deep Web Scraping &bull; RAG &bull; PDF &amp; Audio Export</div>',
    unsafe_allow_html=True
)

# Topic input & presets
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    topic_input = st.text_input(
        "Enter Research Topic:",
        value="AI Agents in 2026",
        placeholder="e.g., Quantum Computing Breakthroughs, Solid-State Batteries, Space Exploration..."
    )

with col_in2:
    st.write("")
    st.write("")
    start_btn = st.button("🚀 Start Autonomous Research", type="primary", use_container_width=True)

# Architecture Features Overview
step_col1, step_col2, step_col3 = st.columns(3)

with step_col1:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge badge-blue">Phase 1 &bull; Discovery</span>
        <div class="step-title">🔎 Search & Deep Scraper</div>
        <div class="step-agent">Agent: Senior Data Researcher</div>
        <div class="step-desc">
            Executes live DuckDuckGo searches and visits top URLs using a custom Deep Webpage Reader to extract technical facts, statistics, and citations.
        </div>
        <div class="step-output">
            <strong>Output:</strong> Verified findings &amp; deep source extracts
        </div>
    </div>
    """, unsafe_allow_html=True)

with step_col2:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge badge-purple">Phase 2 &bull; Synthesis</span>
        <div class="step-title">✍️ Analytical Drafting</div>
        <div class="step-agent">Agent: Reporting Analyst</div>
        <div class="step-desc">
            Ingests raw findings and background documents (RAG), synthesizes technical chapters, analyzes operational impacts, and structures in-depth narratives.
        </div>
        <div class="step-output">
            <strong>Output:</strong> Multi-section comprehensive draft
        </div>
    </div>
    """, unsafe_allow_html=True)

with step_col3:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge badge-emerald">Phase 3 &bull; Final Polish</span>
        <div class="step-title">🛡️ Fact-Check & Executive Brief</div>
        <div class="step-agent">Agent: Lead Editor & Fact-Checker</div>
        <div class="step-desc">
            Audits the draft, eliminates hallucinations, compiles an Executive Summary, Key Takeaways, and renders Markdown, HTML, PDF, and Audio MP3 briefing.
        </div>
        <div class="step-output">
            <strong>Output:</strong> Quad-Format Publication Report
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# System Architecture Highlights
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">3 Agents</div>
        <div class="metric-lbl">Collaborative CrewAI</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">Deep Scraper</div>
        <div class="metric-lbl">Live Webpage Extraction</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">RAG Context</div>
        <div class="metric-lbl">PDF &amp; Knowledge Base</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">Quad Export</div>
        <div class="metric-lbl">MD + HTML + PDF + Audio</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================
# CREW EXECUTION RUNNER
# ==============================================================
if start_btn:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")):
        st.error("❌ Please provide an API Key in `.env` or in the sidebar.")
    elif not topic_input.strip():
        st.warning("⚠️ Please enter a research topic first.")
    else:
        current_year = str(datetime.now().year)

        # Load knowledge base documents
        doc_context = load_knowledge_documents(str(BASE_DIR / "knowledge"))
        knowledge_str = f"Internal Knowledge / Background Documents:\n{doc_context}\n" if doc_context else ""

        inputs = {
            "topic": topic_input.strip(),
            "current_year": current_year,
            "research_depth": research_depth,
            "research_tone": research_tone,
            "knowledge_context": knowledge_str,
        }

        # Status and Live Streaming Container
        with st.status("🚀 **Autonomous Crew Executing...**", expanded=True) as status_box:
            st.write(f"🔬 **Topic:** *{topic_input.strip()}* | **Depth:** {research_depth} | **Tone:** {research_tone}")
            if doc_context:
                st.write("📚 Background knowledge documents successfully attached to agent context.")

            live_stream_placeholder = st.empty()
            redirector = LiveOutputRedirector(live_stream_placeholder)

            try:
                # Run the crew and redirect stdout/stderr to live display
                with contextlib.redirect_stdout(redirector), contextlib.redirect_stderr(redirector):
                    crew_instance = Researcher().crew()
                    result = crew_instance.kickoff(inputs=inputs)

                status_box.update(label="✅ **Research Completed & Reports Exported!**", state="complete", expanded=False)

                report_text = getattr(result, "raw", str(result))
                exported = export_report(report_text, topic=topic_input.strip(), output_dir=str(BASE_DIR / "reports"))

                st.session_state["latest_report"] = report_text
                st.session_state["exported_files"] = exported
                st.session_state["topic_name"] = topic_input.strip()
                st.session_state["chat_history"] = []

            except Exception as e:
                status_box.update(label="❌ Execution Error", state="error", expanded=True)
                st.error(f"Execution Error: {str(e)}")


# ==============================================================
# DISPLAY REPORT & INTERACTIVE WORKBENCH
# ==============================================================
if "latest_report" in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 Research Dossier: {st.session_state.get('topic_name', '')}")

    exported = st.session_state.get("exported_files", {})
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Markdown Report",
        "🌐 HTML Dashboard",
        "💬 Chat with Report",
        "🎧 Audio Podcast Briefing"
    ])

    # Tab 1: Formatted Markdown
    with tab1:
        st.markdown(st.session_state["latest_report"])

    # Tab 2: HTML Preview
    with tab2:
        html_file = exported.get("html_file")
        if html_file and os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)

    # Tab 3: Interactive Follow-up Q&A
    with tab3:
        st.markdown("#### 💬 Ask Follow-up Questions")
        st.caption("Ask questions, request summaries, or drill into specific metrics grounded on the generated report.")

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Display previous chat messages
        for message in st.session_state["chat_history"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input prompt
        user_query = st.chat_input("Ask anything about this research report...")
        if user_query:
            st.session_state["chat_history"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing report..."):
                    answer = answer_report_query(user_query, st.session_state["latest_report"])
                    st.markdown(answer)
                    st.session_state["chat_history"].append({"role": "assistant", "content": answer})

    # Tab 4: Audio Podcast Briefing
    with tab4:
        st.markdown("#### 🎧 Executive Audio Podcast Briefing")
        st.caption("AI-generated voice briefing covering the Executive Summary and Key Takeaways.")

        audio_file = exported.get("audio_file")
        if audio_file and os.path.exists(audio_file):
            st.audio(audio_file)
            with open(audio_file, "rb") as af:
                st.download_button(
                    label="⬇️ Download Audio Brief (.mp3)",
                    data=af.read(),
                    file_name=Path(audio_file).name,
                    mime="audio/mp3"
                )
        else:
            st.info("Audio briefing generation is compiling or unavailable for this session.")

    # Download Center
    st.markdown("---")
    st.markdown("### 📥 Publication Downloads")
    dcol1, dcol2, dcol3, dcol4 = st.columns(4)

    slug_name = st.session_state.get('topic_name', 'research').lower().replace(' ', '_')

    with dcol1:
        st.download_button(
            label="⬇️ Markdown (.md)",
            data=st.session_state["latest_report"],
            file_name=f"report_{slug_name}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with dcol2:
        html_file = exported.get("html_file")
        if html_file and os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                html_bytes = f.read()
            st.download_button(
                label="⬇️ HTML Dashboard (.html)",
                data=html_bytes,
                file_name=f"report_{slug_name}.html",
                mime="text/html",
                use_container_width=True
            )

    with dcol3:
        pdf_file = exported.get("pdf_file")
        if pdf_file and os.path.exists(pdf_file):
            with open(pdf_file, "rb") as pf:
                pdf_bytes = pf.read()
            st.download_button(
                label="⬇️ PDF Document (.pdf)",
                data=pdf_bytes,
                file_name=f"report_{slug_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with dcol4:
        audio_file = exported.get("audio_file")
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, "rb") as af:
                audio_bytes = af.read()
            st.download_button(
                label="⬇️ Audio Brief (.mp3)",
                data=audio_bytes,
                file_name=f"report_{slug_name}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
