# Multi-Agent Research Assistant

A multi-agent system where specialized AI agents collaborate to research a
question, synthesize a cited answer, and fact-check it — producing a
grounded Markdown research report.

## Architecture

```
                ┌─────────────────┐
   question ──> │   Coordinator    │
                └────────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
 │ Search Agent │ │ Summarizer   │ │ Fact-Checker      │
 │              │ │ Agent        │ │ Agent             │
 │ - plans      │ │ - synthesizes│ │ - flags claims    │
 │   sub-queries│ │   cited draft│ │   not backed by   │
 │ - searches   │ │   from raw   │ │   a source        │
 │   the web    │ │   findings   │ │                   │
 └──────────────┘ └──────────────┘ └──────────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                         ▼
                 Final Markdown Report
```

Each agent has a single, narrow responsibility. The **Coordinator**
decides the pipeline order and passes state between agents — this is the
core "agentic" pattern: independent agents with tools/roles, orchestrated
toward a goal, rather than one monolithic LLM call.

## Agents

| Agent | Responsibility |
|---|---|
| **Search Agent** | Breaks the question into sub-queries, searches the web (DuckDuckGo, no API key needed), returns raw findings |
| **Summarizer Agent** | Synthesizes raw findings into a coherent, inline-cited draft answer |
| **Fact-Checker Agent** | Reviews the draft against its cited sources and flags unsupported claims |
| **Coordinator** | Orchestrates the pipeline and assembles the final report |

## Tech stack

- Python
- LangChain (LLM orchestration)
- Groq (GPT-OSS 20B) — free-tier LLM inference (reasoning/generation)
- DuckDuckGo Search (free web search, no API key)

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"
```

## Usage

```bash
python main.py "What are the main approaches to reducing LLM hallucination?"
```

This prints progress from each agent, then saves a full report to `report.md`
with a synthesized answer, fact-check notes, and numbered sources.

## Why this project

This demonstrates the core skills behind agentic AI system design: breaking
a goal into sub-tasks, coordinating multiple specialized agents, grounding
output in real retrieved data, and adding a self-review step — the same
patterns used in production agentic systems for research, support, and
automation.
