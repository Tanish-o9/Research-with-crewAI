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
  1. **Senior Data Researcher:** Conducts live web research and extracts key facts, metrics, and trends.
  2. **Reporting Analyst:** Organizes research into structured chapters and analytical narratives.
  3. **Lead Editor & Fact-Checking Specialist:** Audits accuracy, eliminates repetition, adds an Executive Summary, Key Takeaways, and strategic recommendations.
- 🌐 **Real-time Web Search Tool:** Equipped with a built-in DuckDuckGo Search tool to fetch up-to-date facts without requiring costly search API keys.
- ⌨️ **Dynamic CLI & Interactive Mode:** Run for any topic from the terminal or enter one interactively:
  ```bash
  python src/researcher/main.py "Quantum Computing Breakthroughs"
  ```
- 📊 **Dual Output Format (Markdown + HTML):** Automatically saves timestamped reports and renders a dark-mode styled HTML dashboard view for sharing or presentation.
- 🧠 **Free High-Parameter LLM:** Configured with **NVIDIA Nemotron 3 Super 120B A12B** via OpenRouter.

---

## 🛠️ Tech Stack

- **Framework:** CrewAI 1.14.4
- **Language:** Python `>=3.10, <3.14`
- **Web Search:** `duckduckgo-search`
- **LLM Provider:** OpenRouter (`openrouter/nvidia/nemotron-3-super-120b-a12b:free`)
- **Package Manager:** `uv` / `pip`

---

## 📁 Project Structure

```text
Research-with-crewAI/
├── knowledge/
│   └── user_preference.txt           # Sample knowledge base context
├── reports/
│   └── .gitkeep                      # Output directory for generated reports
├── src/
│   └── researcher/
│       ├── config/
│       │   ├── agents.yaml           # Agent roles, backstories, models
│       │   └── tasks.yaml            # Task instructions, outputs, assignments
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── custom_tool.py        # Custom tool scaffold
│       │   ├── export_utils.py       # Dual Markdown & HTML export engine
│       │   └── search_tool.py        # Live DuckDuckGo web search tool
│       ├── __init__.py
│       ├── crew.py                   # Sequential crew orchestration
│       └── main.py                   # Dynamic CLI entrypoint
├── tests/
│   ├── __init__.py
│   └── test_crew.py                  # Unit tests for crew and tools
├── .env.example
├── .gitignore
├── .python-version
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

### Option A: Pass a topic via CLI
```bash
python src/researcher/main.py "Artificial General Intelligence"
```

### Option B: Interactive mode
```bash
python src/researcher/main.py
```
*(Prompts: `Enter research topic (Press Enter for 'AI LLMs'):`)*

### Option C: CrewAI CLI
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
