# ⚡ Autonomous Multi-Agent Research Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Groq LPU](https://img.shields.io/badge/Inference-Groq_LPU-f55036.svg)](https://groq.com)
[![LangChain](https://img.shields.io/badge/Orchestration-LangChain-green.svg)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade **Multi-Agent Research System** that autonomously decomposes complex research questions, queries real-time web knowledge, synthesizes structured inline-cited dossiers, and executes self-critique fact-checking before final delivery.

Built for speed and precision using **Groq LPUs (LLaMA 3.3 70B)**, **LangChain agentic orchestration**, and **DuckDuckGo zero-key search**.

---

## 🌟 Key Highlights

- **🎯 True Multi-Agent Orchestration**: Deconstructs monolithic LLM prompts into specialized, single-responsibility agents with clean boundaries and state governance.
- **🔍 Zero-Key Web Search Tool**: Multi-threaded, resilient web intelligence gathering using DuckDuckGo scraping backends with automatic retries and deduplication.
- **🛡️ Self-Critique & Grounding Gate**: A dedicated Fact-Checker agent cross-references synthesized draft assertions against raw source snippets to flag hallucinations.
- **⚡ Ultra-Fast Inference via Groq**: Delivers comprehensive research dossiers in ~4-6 seconds using high-throughput LLaMA 3.3 70B inference.
- **💼 Portfolio-Ready Web UI**: Interactive Streamlit interface featuring a real-time agent execution stepper, interactive source cards, citations inspector, and JSON/Markdown exports.

---

## 🏛️ System Architecture

```
                                 ┌───────────────────────┐
                     Topic ────> │   Coordinator Agent   │
                                 └───────────┬───────────┘
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │                     │                     │
                       ▼                     ▼                     ▼
              ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
              │  Search Agent   │   │ Summarizer Agent│   │Fact-Checker Agt │
              │                 │   │                 │   │                 │
              │ • Sub-query     │   │ • Cross-source  │   │ • Verifies draft│
              │   decomposition │   │   synthesis     │   │   claims against│
              │ • Multi-query   │   │ • Inline numeric│   │   source context│
              │   web search    │   │   citations [1] │   │ • Flags unbacked│
              │ • Deduplication │   │ • Markdown draft│   │   assertions    │
              └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
                       │                     │                     │
                       └─────────────────────┼─────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Verified Research Dossier │
                               │ (.md / .json / Web UI)    │
                               └───────────────────────────┘
```

### Agent Roles & Responsibilities

| Agent | Responsibility | Core Mechanism |
|---|---|---|
| **🎯 Coordinator** | Orchestrates pipeline workflow, sequences state transitions, and formats final executive dossier | Pipeline state machine & callback logger |
| **🔍 Search Agent** | Expands topic into $N$ targeted sub-queries and aggregates web intelligence | Prompt-guided decomposition + DuckDuckGo |
| **📝 Summarizer** | Synthesizes raw findings into a cohesive, structured answer with inline numerical citations `[1]` | Grounded in-context synthesis |
| **🛡️ Fact-Checker** | Acts as an independent quality gate, checking synthesized claims against retrieved source snippets | Invariant verification prompt |

---

## 🚀 Quickstart & Local Setup

### 1. Clone Repository & Install Dependencies

```bash
git clone https://github.com/Mohamedislam42/multi-agent-research-assistant.git
cd multi-agent-research-assistant

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file or set the environment variable:

```bash
cp .env.example .env
```

Add your free Groq API key:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(Get a free, instant Groq API key at [console.groq.com/keys](https://console.groq.com/keys))*

---

## 🖥️ Running the Application

### Option A: Interactive Web UI (Streamlit)

```bash
streamlit run app.py
```
Open `http://localhost:8501` to run custom research questions with live multi-agent execution visualizers.

### Option B: Command-Line Interface (CLI)

```bash
# Basic usage
python main.py "What are the latest breakthroughs in Graph RAG architectures?"

# Custom model and subqueries
python main.py --model llama-3.3-70b-versatile --subqueries 4 "Autonomous AI Agents in Software Engineering"
```
The output is displayed in the terminal and saved to `report.md`.

---

## ☁️ Deployment Guide

### Deploying to Streamlit Community Cloud (Recommended — Free & 1-Click)

1. **Fork or Push** this repository to your GitHub account (`https://github.com/Mohamedislam42/multi-agent-research-assistant`).
2. Log in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **"New app"** and select:
   - **Repository:** `Mohamedislam42/multi-agent-research-assistant`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Expand **Advanced settings > Secrets** and enter:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key"
   ```
5. Click **Deploy!** Your app will be live with a shareable URL (e.g. `https://your-app.streamlit.app`).

### Deploying with Docker

```bash
# Build Docker image
docker build -t research-assistant .

# Run container
docker run -p 8501:8501 -e GROQ_API_KEY="your-groq-key" research-assistant
```

---

## 📂 Project Structure

```
├── agents/
│   ├── coordinator.py       # Orchestration logic, timing & structured outputs
│   ├── search_agent.py      # Sub-query planner & search harvester
│   ├── summarizer_agent.py  # Grounded synthesis & citation generator
│   └── fact_checker_agent.py# Verification quality gate & hallucination audit
├── tools/
│   └── web_search.py        # Resilient DuckDuckGo web scraper with fallbacks
├── .streamlit/
│   └── config.toml          # Custom dark slate & indigo theme configuration
├── app.py                   # Portfolio-grade Streamlit web application
├── main.py                  # CLI entry point with argparse support
├── Dockerfile               # Production container definition
├── requirements.txt         # Pinned python dependencies
├── .env.example             # Environment template
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```


---

## 🛠️ Tech Stack & Tools

- **Core Engine:** Python 3.10+, LangChain
- **LLM Inference:** [Groq Cloud](https://groq.com) (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`)
- **Web Intelligence:** DuckDuckGo Search (`ddgs`)
- **Frontend / Dashboard:** Streamlit
- **Deployment:** Streamlit Cloud / Docker

---

## 👤 Author & Portfolio

**Mohamed Islam**  
- **GitHub:** [@Mohamedislam42](https://github.com/Mohamedislam42)  
- **Project Repository:** [multi-agent-research-assistant](https://github.com/Mohamedislam42/multi-agent-research-assistant)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
