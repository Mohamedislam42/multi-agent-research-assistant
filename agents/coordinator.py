"""
Coordinator

Orchestrates the full multi-agent pipeline:
  SearchAgent -> SummarizerAgent -> FactCheckerAgent -> final report

This is the "agentic" backbone: each agent has a narrow responsibility,
and the coordinator decides the sequence and assembles the final output.
"""

from datetime import datetime

from langchain_groq import ChatGroq

from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.fact_checker_agent import FactCheckerAgent


class Coordinator:
    def __init__(self, model: str = "openai/gpt-oss-20b"):
        llm = ChatGroq(model=model, temperature=0)
        self.search_agent = SearchAgent(llm)
        self.summarizer_agent = SummarizerAgent(llm)
        self.fact_checker_agent = FactCheckerAgent(llm)

    def run(self, question: str) -> str:
        print(f"\n[Coordinator] Researching: {question}\n")

        # Step 1: gather raw findings from the web
        findings = self.search_agent.run(question)
        print(f"[Coordinator] Collected {len(findings)} raw findings.")

        # Step 2: synthesize into a cited draft
        draft, sources = self.summarizer_agent.run(question, findings)
        print("[Coordinator] Draft synthesized.")

        # Step 3: fact-check the draft against sources
        flags = self.fact_checker_agent.run(draft, sources)
        print("[Coordinator] Fact-check complete.")

        # Step 4: assemble final report
        report = self._assemble_report(question, draft, sources, flags)
        return report

    def _assemble_report(self, question, draft, sources, flags) -> str:
        source_lines = [f"[{s['id']}] {s['title']} — {s['url']}" for s in sources]
        return f"""# Research Report

**Question:** {question}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Answer

{draft}

## Fact-Check Notes

{flags}

## Sources

{chr(10).join(source_lines)}
"""
