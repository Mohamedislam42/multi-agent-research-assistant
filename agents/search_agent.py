"""
Search Agent

Responsible for gathering raw information from the web relevant to the
user's research question. Breaks the question into a few sub-queries so
coverage is broader than a single search.
"""

from langchain_groq import ChatGroq

from tools.web_search import web_search


SUBQUERY_PROMPT = """You are a research planning assistant.
Given a research question, produce 3 distinct, specific web search queries
that together would give good coverage of the topic.
Return ONLY the 3 queries, one per line, no numbering.

Research question: {question}
"""


class SearchAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm

    def plan_subqueries(self, question: str) -> list[str]:
        prompt = SUBQUERY_PROMPT.format(question=question)
        response = self.llm.invoke(prompt)
        lines = [line.strip("- ").strip() for line in response.content.split("\n")]
        return [line for line in lines if line][:3]

    def run(self, question: str) -> list[dict]:
        """Search the web across a few sub-queries and return combined findings."""
        subqueries = self.plan_subqueries(question)
        print(f"[SearchAgent] Sub-queries: {subqueries}")

        findings = []
        for query in subqueries:
            results = web_search(query, max_results=4)
            for r in results:
                r["query"] = query
                findings.append(r)
        return findings
