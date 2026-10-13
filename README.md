# 🔍 Researcher with CrewAI

An advanced multi-agent research and intelligence pipeline built with **CrewAI** and Large Language Models (LLMs). It coordinates three specialized AI agents to autonomously search the web, synthesize findings, verify facts, and produce publication-ready research reports in both **Markdown** and **HTML Dashboard** formats.

---

## 🚀 Overview

Instead of relying on a single prompt or a generic LLM response, **Researcher with CrewAI** orchestrates a sequential, multi-agent editorial pipeline:

```text
User Topic Input (CLI / Interactive)
                 │
                 ▼
┌──────────────────────────────────────┐
│       Senior Data Researcher         │ ◄─── Uses Live Web Search Tool
└──────────────────────────────────────┘      (DuckDuckGo Search)
                 │
                 ▼ (Passes 10 Key Findings + Sources)
┌──────────────────────────────────────┐
│          Reporting Analyst           │ ────► Drafts In-depth Sections
└──────────────────────────────────────┘
                 │
                 ▼ (Passes Draft Report)
┌──────────────────────────────────────┐
│  Lead Editor & Fact-Checking Expert  │ ────► Polishes, Adds Executive Summary,
└──────────────────────────────────────┘      Key Takeaways & Citations
                 │
                 ▼
┌──────────────────────────────────────┐
│             Dual Export              │ ────► 📄 reports/report_*.md
│                                      │ ────► 🌐 reports/report_*.html
└──────────────────────────────────────┘
```

---

## ✨ Key Features

- 🤖 **3-Agent Pipeline:**
  1. **Senior Data Researcher:** Conducts live web research via DuckDuckGo and uses deep web scraping to extract full articles and data.
  2. **Reporting Analyst:** Ingests research findings and local knowledge base documents (RAG) to draft structured chapters.
  3. **Lead Editor & Fact-Checking Specialist:** Audits accuracy, eliminates repetition, adds an Executive Summary, Key Takeaways, and strategic recommendations.
- 🌐 **Deep Web Scraping & Live Search:** Equipped with DuckDuckGo Search and a custom `PageScraperTool` (`read_webpage_content`) to visit URLs and extract full body content.
- 📁 **Knowledge Base & Document Upload (RAG):** Upload PDF, TXT, and MD documents in the Streamlit UI to ground research on internal reference material alongside live web data.
- 💬 **Interactive "Chat with Report":** Follow-up Q&A assistant tab in Streamlit grounded strictly on the generated report.
- 🎧 **Executive Audio Podcast Briefing:** Automatically generates an MP3 audio briefing using text-to-speech for hands-free listening.
- 📊 **Quad-Format Export (Markdown + HTML + PDF + MP3):** Exports timestamped `.md`, dark-mode `.html` dashboard, formatted `.pdf` document, and `.mp3` audio briefing.
- ⚡ **Live Real-time Agent Streaming:** Watch agents think, search, scrape, and draft live on the Streamlit dashboard console.

---

## 🛠️ Tech Stack

- **Framework:** CrewAI 1.15+
- **Language:** Python `>=3.10, <3.14`
- **Web Search & Scraping:** `duckduckgo-search`, `beautifulsoup4`, `requests`
- **Document RAG:** `pypdf`
- **PDF Publishing:** `reportlab`
- **Voice Briefing:** `gTTS` / `pyttsx3`
- **LLM Engine:** Google Gemini (`gemini-2.5-flash`) / OpenRouter
- **User Interface:** Streamlit

---

## 📁 Project Structure

```text
Researcher-with-CrewAI/
├── knowledge/
│   └── user_preference.txt           # Ingested knowledge documents (PDF, TXT, MD)
├── reports/
│   └── .gitkeep                      # Output directory (.md, .html, .pdf, .mp3)
├── src/
│   └── researcher/
│       ├── config/
│       │   ├── agents.yaml           # Agent roles, backstories, models
│       │   └── tasks.yaml            # Task instructions, depth, tone & knowledge
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── audio_brief.py        # Audio podcast briefing generator (TTS)
│       │   ├── custom_tool.py        # Custom tool scaffold
│       │   ├── export_utils.py       # Quad export engine (MD, HTML, PDF, MP3)
│       │   ├── knowledge_utils.py    # PDF and text document RAG loader
│       │   ├── pdf_export.py         # ReportLab publication PDF generator
│       │   ├── scraper_tool.py       # Deep webpage content reader
│       │   └── search_tool.py        # Live DuckDuckGo web search tool
│       ├── __init__.py
│       ├── crew.py                   # Sequential crew orchestration
│       └── main.py                   # Dynamic CLI entrypoint
├── tests/
│   ├── __init__.py
│   └── test_crew.py                  # Unit tests for crew, tools, PDF, audio & RAG
├── .env.example
├── .gitignore
├── .python-version
├── app.py                            # Streamlit Web UI Dashboard with streaming & chat
├── AGENTS.md                         # CrewAI developer reference guide
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 📦 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Tanish-o9/Research-with-crewAI.git
cd Research-with-crewAI
```

### 2. Install dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using standard `pip`:
```bash
pip install -e .
```

### 3. Configure API Key

Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

*(Get a free key from [OpenRouter](https://openrouter.ai/keys)).*

---

## 🚀 Running the Project

### Option A: Interactive Streamlit Web UI (Recommended)
Launch the graphical browser interface:
```bash
streamlit run app.py
```

### Option B: Pass a topic via CLI
```bash
python src/researcher/main.py "Artificial General Intelligence"
```

### Option C: Interactive Terminal mode
```bash
python src/researcher/main.py
```
*(Prompts: `Enter research topic (Press Enter for 'AI LLMs'):`)*

### Option D: CrewAI CLI
```bash
crewai run
```

---

## 📊 Output

Generated reports are automatically saved inside the `reports/` folder:
- **`reports/report_<timestamp>_<topic>.md`** — Clean Markdown report.
- **`reports/report_<timestamp>_<topic>.html`** — Styled HTML dashboard view ready to open in any web browser.
- **`reports/latest_report.md`** — Symlink/copy of the most recent run.

---

## 👨‍💻 Author

**Tanish Kumar**  
GitHub: [https://github.com/Tanish-o9](https://github.com/Tanish-o9)

---

## 📄 License

This project is licensed under the MIT License.
