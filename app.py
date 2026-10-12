import os
import sys
from datetime import datetime
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Ensure 'src' is accessible in sys.path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv()
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from researcher.crew import Researcher
from researcher.tools.export_utils import export_report

# Page Configuration
st.set_page_config(
    page_title="Researcher with CrewAI",
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


# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Settings & Status")

    # API Key check
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if gemini_key:
        st.success("✅ Gemini 2.5 Flash Active")
    elif openrouter_key:
        st.success("✅ OpenRouter API Key Active")
    else:
        st.warning("⚠️ No API Key found in .env")
        custom_key = st.text_input("Enter Gemini API Key", type="password")
        if custom_key:
            os.environ["GEMINI_API_KEY"] = custom_key
            os.environ["GOOGLE_API_KEY"] = custom_key
            st.success("API Key updated for this session!")

    st.markdown("---")
    st.subheader("🤖 Active Crew Agents")
    st.markdown("""
    - **🔍 Senior Data Researcher**  
      *Real-time web search with DuckDuckGo*
    - **✍️ Reporting Analyst**  
      *Detailed chapter & narrative drafting*
    - **🛡️ Lead Editor & Fact-Checker**  
      *Audit, Executive Summary & Takeaways*
    """)

    st.markdown("---")
    st.subheader("📚 Saved Reports History")
    reports_dir = BASE_DIR / "reports"
    if reports_dir.exists():
        md_files = sorted(list(reports_dir.glob("report_*.md")), reverse=True)
        if md_files:
            selected_file = st.selectbox(
                "Select a previous report to view:",
                options=md_files,
                format_func=lambda x: x.stem.replace("report_", "")
            )
            if selected_file:
                with open(selected_file, "r", encoding="utf-8") as f:
                    past_content = f.read()
                st.download_button(
                    label="📥 Download Selected Report",
                    data=past_content,
                    file_name=selected_file.name,
                    mime="text/markdown"
                )
        else:
            st.info("No past reports found yet.")
    else:
        st.info("Reports folder will appear after first run.")


# Main App Layout
st.markdown('<div class="main-title">🔍 AI Research & Intelligence Crew</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Autonomous 3-Agent Collaborative Research Pipeline powered by CrewAI &amp; Google Gemini</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([3, 1])

with col1:
    default_topic = "AI Agents in 2026"
    topic_input = st.text_input(
        "Enter Research Topic:",
        value=default_topic,
        placeholder="e.g., Quantum Computing Breakthroughs, Solid-State Batteries, Space Exploration..."
    )

with col2:
    st.write("")
    st.write("")
    start_btn = st.button("🚀 Start Autonomous Research", type="primary", use_container_width=True)

# ----------------- HOW AGENTS WORK SECTION -----------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### ⚡ How the Multi-Agent Pipeline Works")

step_col1, step_col2, step_col3 = st.columns(3)

with step_col1:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge badge-blue">Phase 1 &bull; Discovery</span>
        <div class="step-title">🔎 Live Web Research</div>
        <div class="step-agent">Agent: Senior Data Researcher</div>
        <div class="step-desc">
            Executes autonomous real-time web searches using DuckDuckGo to unearth primary sources, latest breakthrough metrics, and current year trends.
        </div>
        <div class="step-output">
            <strong>Output:</strong> 10 Verified Key Findings with citations
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
            Takes raw research findings as context, dissects technical nuances, analyzes industry impact, and synthesizes in-depth multi-section chapters.
        </div>
        <div class="step-output">
            <strong>Output:</strong> Comprehensive Draft Technical Report
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
            Audits the report for consistency and clarity, eliminates hallucinations, crafts a high-impact Executive Summary, Key Takeaways, and strategic recommendations.
        </div>
        <div class="step-output">
            <strong>Output:</strong> Publication-ready Markdown & HTML Dashboard
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
        <div class="metric-lbl">Autonomous Collaboration</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">Gemini 2.5</div>
        <div class="metric-lbl">High-Speed Flash Engine</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">Live Web</div>
        <div class="metric-lbl">Real-Time Search Retrieval</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown("""
    <div class="metric-badge">
        <div class="metric-val">MD + HTML</div>
        <div class="metric-lbl">Dual Multi-Format Export</div>
    </div>
    """, unsafe_allow_html=True)


# ----------------- RUN CREW EXECUTION -----------------
if start_btn:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENROUTER_API_KEY")):
        st.error("❌ Please provide an API Key in `.env` or in the sidebar.")
    elif not topic_input.strip():
        st.warning("⚠️ Please enter a research topic first.")
    else:
        current_year = str(datetime.now().year)
        inputs = {
            "topic": topic_input.strip(),
            "current_year": current_year
        }

        progress_container = st.container()
        with progress_container:
            st.info(f"⏳ **Crew kicked off for:** '{topic_input.strip()}'. Running 3 sequential agents...")
            progress_bar = st.progress(15)

            status_text = st.empty()
            status_text.markdown("🔎 **Step 1/3:** Senior Data Researcher searching the live web for verified data...")

            try:
                # Instantiate and kickoff the crew
                crew_instance = Researcher().crew()
                result = crew_instance.kickoff(inputs=inputs)

                progress_bar.progress(85)
                status_text.markdown("🛡️ **Step 3/3:** Fact-Checker finalizing Executive Summary & exporting...")

                report_text = getattr(result, "raw", str(result))
                exported = export_report(report_text, topic=topic_input.strip())

                progress_bar.progress(100)
                status_text.markdown("✅ **Research Complete!**")

                st.session_state["latest_report"] = report_text
                st.session_state["exported_files"] = exported
                st.session_state["topic_name"] = topic_input.strip()

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# Display Report if available
if "latest_report" in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 Research Report: {st.session_state.get('topic_name', '')}")

    exported = st.session_state.get("exported_files", {})
    tab1, tab2 = st.tabs(["📄 Formatted Markdown Report", "🌐 HTML Preview"])

    with tab1:
        st.markdown(st.session_state["latest_report"])

    with tab2:
        html_file = exported.get("html_file")
        if html_file and os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)

    # Download Buttons
    st.markdown("### 📥 Download Outputs")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            label="⬇️ Download Markdown (.md)",
            data=st.session_state["latest_report"],
            file_name=f"report_{st.session_state.get('topic_name', 'research').lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with dcol2:
        html_file = exported.get("html_file")
        if html_file and os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                html_bytes = f.read()
            st.download_button(
                label="⬇️ Download HTML Dashboard (.html)",
                data=html_bytes,
                file_name=f"report_{st.session_state.get('topic_name', 'research').lower().replace(' ', '_')}.html",
                mime="text/html",
                use_container_width=True
            )
