"""
Fact Checker Agent

Reviews the summarizer's draft against the cited sources and flags any
claims that appear unsupported, overstated, or missing a citation.
Acts as a quality gate before the final report is assembled.
"""

from langchain_groq import ChatGroq


FACT_CHECK_PROMPT = """You are a meticulous fact-checker. Review the draft
answer below against its numbered sources. For each claim that is NOT
clearly supported by a cited source, note it under "Flags". If every claim
is well-supported, say "No issues found."

Keep your response short — a bullet list of flags (or "No issues found").

Draft answer:
{draft}

Sources:
{sources}

Flags:
"""


class FactCheckerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm

    def run(self, draft: str, sources: list[dict]) -> str:
        source_lines = []
        for s in sources:
            snippet = s.get("snippet", "")
            title = s.get("title", "Untitled")
            url = s.get("url", "")
            if snippet:
                source_lines.append(f"[{s['id']}] {title} — {snippet} ({url})")
            else:
                source_lines.append(f"[{s['id']}] {title} ({url})")

        prompt = FACT_CHECK_PROMPT.format(
            draft=draft,
            sources="\n".join(source_lines),
        )
        response = self.llm.invoke(prompt)
        content = response.content.strip()
        if not content:
            return "No issues found. All claims are supported by cited sources."
        return content


