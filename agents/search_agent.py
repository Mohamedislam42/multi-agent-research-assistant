"""
Search Agent

Responsible for gathering raw information from the web relevant to the
user's research question. Breaks the question into a few sub-queries so
coverage is broader than a single search.
"""

from langchain_groq import ChatGroq

from tools.web_search import web_search


SUBQUERY_PROMPT = """You are a research planning assistant.
Given a research question, produce {num_queries} distinct, specific web search queries
that together would give comprehensive coverage of the topic.
Return ONLY the search queries, one per line, with no numbering, bullet points, or extra text.

Research question: {question}
"""


class SearchAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm

    def plan_subqueries(self, question: str, num_queries: int = 3) -> list[str]:
        prompt = SUBQUERY_PROMPT.format(question=question, num_queries=num_queries)
        response = self.llm.invoke(prompt)
        raw_lines = response.content.strip().split("\n")
        
        cleaned = []
        for line in raw_lines:
            line = line.strip().lstrip("0123456789.-*• \t\"'").rstrip("\"'")
            if line and len(line) > 3 and not line.lower().startswith("here are"):
                cleaned.append(line)

        return cleaned[:num_queries] if cleaned else [question]

    def run(
        self,
        question: str,
        num_queries: int = 3,
        max_results_per_query: int = 4,
        on_query_complete=None,
    ) -> tuple[list[dict], list[str]]:
        """Search the web across sub-queries and return (findings, subqueries)."""
        subqueries = self.plan_subqueries(question, num_queries=num_queries)
        print(f"[SearchAgent] Sub-queries planned: {subqueries}")

        findings = []
        seen_urls = set()

        for query in subqueries:
            results = web_search(query, max_results=max_results_per_query)
            query_results = []
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    r["query"] = query
                    findings.append(r)
                    query_results.append(r)
                elif not url:
                    r["query"] = query
                    findings.append(r)
                    query_results.append(r)
            
            if on_query_complete:
                on_query_complete(query, query_results)

        return findings, subqueries

