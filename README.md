# 🔍 Researcher with CrewAI

An AI-powered research automation project built using **CrewAI** and Large Language Models (LLMs). It uses specialized AI agents to research topics, analyze information, and generate structured research reports through a collaborative workflow.

## 🚀 Overview

Research with CrewAI demonstrates how multiple AI agents can work together to automate a research task. Instead of relying on a single AI agent, the project separates research and report writing into specialized tasks.

The workflow takes a research topic as input, gathers relevant findings, and generates a structured report in Markdown format.

## ✨ Features

- 🤖 **Multi-Agent Workflow:** Uses specialized AI agents for different responsibilities.
- 🔎 **Automated Research:** Researches the given topic and identifies key findings.
- 📝 **Report Generation:** Creates structured research reports automatically.
- 🔗 **Task Coordination:** Passes research findings between sequential tasks.
- 🧠 **LLM Integration:** Uses a language model through OpenRouter.
- 📄 **Markdown Output:** Generates a readable research report.

## 🛠️ Tech Stack

- **Language:** Python
- **Multi-Agent Framework:** CrewAI
- **LLM Access:** OpenRouter
- **Configuration:** YAML
- **Package Management:** uv

## ⚙️ How It Works

1. **Input:** The user provides a research topic.
2. **Research Agent:** Collects information and identifies important findings.
3. **Reporting Agent:** Organizes the findings into a structured report.
4. **Output:** The final report is generated as a Markdown file.

## 📁 Project Structure

```text
Research-with-CrewAI/
├── knowledge/
│   └── user_preference.txt
├── src/
│   └── researcher/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── tools/
│       │   ├── __init__.py
│       │   └── custom_tool.py
│       ├── __init__.py
│       ├── crew.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_crew.py
├── .env.example
├── .gitignore
├── .python-version
├── AGENTS.md
├── pyproject.toml
├── uv.lock
└── README.md
```

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Tanish-o9/Research-with-crewAI.git
cd Research-with-crewAI
```

### 2. Install dependencies

If the project uses `uv`, install it and sync the dependencies:

```bash
pip install uv
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

Replace the placeholder with your own API key. Never commit real API keys to GitHub.

### 4. Run the project

Use the command specified in the repository's entry point and configuration. For example:

```bash
uv run main.py
```

If the project expects a different command or requires a topic through a specific input mechanism, follow its current `README`, `main.py`, and `pyproject.toml` configuration.

## 📊 Output

The system generates a structured research report containing key findings and explanations about the selected topic.

The report can be saved in Markdown format and viewed in any Markdown editor.

## 🎯 Learning Objectives

This project helps demonstrate practical concepts such as:

- AI agents and agent roles
- Task definition and execution
- Sequential multi-agent workflows
- Context passing between tasks
- LLM API integration
- Automated report generation

## 🔮 Future Improvements

- Add web-search tools for source-based research.
- Introduce a fact-checking agent.
- Include source links and citations in reports.
- Add parallel research agents.
- Build a web interface using FastAPI and React.
- Add report evaluation and quality checks.

## 🔐 Security

- Store API keys in environment variables.
- Keep `.env` out of version control.
- Never expose private credentials in source code or public commits.

## 📌 Project Status

This project is a learning-oriented implementation of an AI research workflow using CrewAI. Its capabilities depend on the configured agents, tools, and language model.

## 👨‍💻 Author

**Your Name**

GitHub: https://github.com/Tanish-o9

## 📄 License

Add a license if you intend to distribute or reuse this project under specific terms.
