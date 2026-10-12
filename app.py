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
    .agent-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .report-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/artificial-intelligence.png", width=70)
    st.title("Settings & Status")

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
    '<div class="sub-title">Autonomous 3-Agent Collaborative Research Pipeline powered by CrewAI &amp; OpenRouter</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([3, 1])

with col1:
    default_topic = "AI Agents in 2026"
    topic_input = st.text_input(
        "Enter Research Topic:",
        value=default_topic,
        placeholder="e.g., Quantum Computing Breakthroughs, Solid-State Batteries..."
    )

with col2:
    st.write("")
    st.write("")
    start_btn = st.button("🚀 Start Autonomous Research", type="primary", use_container_width=True)

# Preset Suggestions
st.markdown("**Quick Topics:**")
cols = st.columns(4)
if cols[0].button("🧬 mRNA Vaccines 2026"):
    st.session_state["topic"] = "mRNA Vaccines Breakthroughs in 2026"
    st.rerun()
if cols[1].button("⚛️ Quantum Computing"):
    st.session_state["topic"] = "Quantum Computing Advancements in 2026"
    st.rerun()
if cols[2].button("🔋 Solid-State Batteries"):
    st.session_state["topic"] = "Commercial Solid-State Battery Progress in 2026"
    st.rerun()
if cols[3].button("🤖 Humanoid Robots"):
    st.session_state["topic"] = "Commercial Humanoid Robotics Industry in 2026"
    st.rerun()

if "topic" in st.session_state:
    topic_input = st.session_state["topic"]


# Run Crew Execution
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
