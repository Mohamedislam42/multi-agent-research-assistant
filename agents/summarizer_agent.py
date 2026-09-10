"""
Summarizer Agent

Takes raw search findings (titles, URLs, snippets) and synthesizes them
into a coherent draft answer to the original research question.
"""

from langchain_groq import ChatGroq


SUMMARY_PROMPT = """You are a research analyst. Using ONLY the source material
below, write a clear, well-organized draft answer to the research question.
Cite sources inline using [1], [2], etc. matching the numbered list below.
Do not invent information that isn't supported by the sources.

Research question: {question}

Sources:
{sources}

Draft answer:
"""


class SummarizerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm

    def run(self, question: str, findings: list[dict]) -> tuple[str, list[dict]]:
        numbered_sources = []
        source_lines = []
        for i, f in enumerate(findings, start=1):
            snippet = f.get("snippet", "").strip()
            title = f.get("title", "Untitled Source").strip()
            url = f.get("url", "")
            query = f.get("query", "")
            
            source_lines.append(f"[{i}] {title} — {snippet} ({url})")
            numbered_sources.append({
                "id": i,
                "title": title,
                "url": url,
                "snippet": snippet,
                "query": query,
            })

        prompt = SUMMARY_PROMPT.format(
            question=question,
            sources="\n".join(source_lines),
        )
        response = self.llm.invoke(prompt)
        return response.content, numbered_sources

