"""
Coordinator

Orchestrates the full multi-agent pipeline:
  SearchAgent -> SummarizerAgent -> FactCheckerAgent -> final report

This is the "agentic" backbone: each agent has a narrow responsibility,
and the coordinator decides the sequence and assembles the final output.
"""

import os
import time
from datetime import datetime
from typing import Callable, Optional

# Load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_groq import ChatGroq

from agents.search_agent import SearchAgent
from agents.summarizer_agent import SummarizerAgent
from agents.fact_checker_agent import FactCheckerAgent


DEFAULT_MODEL = "openai/gpt-oss-20b"
FALLBACK_MODEL = "openai/gpt-oss-120b"


class Coordinator:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        temperature: float = 0.0,
    ):
        groq_api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    groq_api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass

        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Please set the GROQ_API_KEY environment variable or Streamlit secret."
            )

        self.api_key = groq_api_key
        os.environ["GROQ_API_KEY"] = self.api_key
        self.model = model
        self.temperature = temperature

        try:
            llm = ChatGroq(
                model=self.model,
                groq_api_key=self.api_key,
                temperature=self.temperature,
            )
        except Exception as e:
            print(f"[Coordinator] Warning: Failed with model '{model}', falling back to '{FALLBACK_MODEL}': {e}")
            self.model = FALLBACK_MODEL
            llm = ChatGroq(
                model=self.model,
                groq_api_key=self.api_key,
                temperature=self.temperature,
            )

        self.search_agent = SearchAgent(llm)
        self.summarizer_agent = SummarizerAgent(llm)
        self.fact_checker_agent = FactCheckerAgent(llm)

    def run(
        self,
        question: str,
        num_queries: int = 3,
        max_results_per_query: int = 4,
        on_step: Optional[Callable[[str, str, dict], None]] = None,
        return_details: bool = False,
    ):
        """Execute the multi-agent research pipeline."""
        start_time = time.time()
        print(f"\n[Coordinator] Researching: {question}\n")

        # Step 1: Search Agent
        if on_step:
            on_step("SearchAgent", "planning", {"message": "Deconstructing research question into sub-queries..."})

        findings, subqueries = self.search_agent.run(
            question=question,
            num_queries=num_queries,
            max_results_per_query=max_results_per_query,
            on_query_complete=lambda q, res: on_step("SearchAgent", "query_complete", {"query": q, "results_count": len(res)}) if on_step else None,
        )
        print(f"[Coordinator] Collected {len(findings)} raw findings across {len(subqueries)} sub-queries.")

        if on_step:
            on_step("SearchAgent", "complete", {
                "subqueries": subqueries,
                "findings_count": len(findings),
                "findings": findings,
            })

        # Step 2: Summarizer Agent
        if on_step:
            on_step("SummarizerAgent", "synthesizing", {"message": "Synthesizing inline-cited draft from raw findings..."})

        draft, sources = self.summarizer_agent.run(question, findings)
        print("[Coordinator] Draft synthesized.")

        if on_step:
            on_step("SummarizerAgent", "complete", {
                "draft": draft,
                "sources_count": len(sources),
                "sources": sources,
            })

        # Step 3: Fact-Checker Agent
        if on_step:
            on_step("FactCheckerAgent", "verifying", {"message": "Verifying draft claims against source citations..."})

        flags = self.fact_checker_agent.run(draft, sources)
        print("[Coordinator] Fact-check complete.")

        if on_step:
            on_step("FactCheckerAgent", "complete", {
                "flags": flags,
            })

        # Step 4: Assemble final report
        elapsed_seconds = round(time.time() - start_time, 2)
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        report = self._assemble_report(question, draft, sources, flags, timestamp_str)

        if on_step:
            on_step("Coordinator", "complete", {
                "report": report,
                "elapsed_seconds": elapsed_seconds,
            })

        if return_details:
            return {
                "question": question,
                "report": report,
                "draft": draft,
                "sources": sources,
                "findings": findings,
                "subqueries": subqueries,
                "flags": flags,
                "model": self.model,
                "elapsed_seconds": elapsed_seconds,
                "timestamp": timestamp_str,
            }

        return report

    def _assemble_report(self, question: str, draft: str, sources: list[dict], flags: str, timestamp: str) -> str:
        source_lines = [f"[{s['id']}] [{s['title']}]({s['url']})" if s.get("url") else f"[{s['id']}] {s['title']}" for s in sources]
        
        flag_status = "✅ Verified - No unsupported claims detected" if "no issues found" in flags.lower() else "⚠️ Quality Flags Identified"

        return f"""# Research Dossier: {question}

**Status:** {flag_status}  
**Model:** `{self.model}` | **Generated:** {timestamp}

---

## Executive Summary & Findings

{draft}

---

## Fact-Check & Verification Audit

{flags}

---

## References & Grounded Sources

{chr(10).join(source_lines) if source_lines else "No external sources recorded."}
"""
