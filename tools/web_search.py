"""
Web search tool used by the Search Agent.

Uses DuckDuckGo (via the `ddgs` package — the renamed successor to
`duckduckgo-search`) so the project runs with zero extra API keys beyond
the LLM provider. Includes basic retry logic since the backend
occasionally times out or rate-limits, and falls back across DuckDuckGo's
different backends if one returns nothing useful.
"""

import time

from ddgs import DDGS

# Try backends in order; "lite" can return stale/irrelevant cached results
# on some networks, so prefer "html" (the standard scraped backend) first.
BACKENDS = ["html", "lite", "api"]


def web_search(query: str, max_results: int = 5, retries: int = 2) -> list[dict]:
    """Run a web search and return a list of {title, url, snippet} results.

    Tries multiple backends and retries with a short backoff, since
    DuckDuckGo's free scraping backends are occasionally flaky.
    """
    for backend in BACKENDS:
        for attempt in range(1, retries + 1):
            try:
                results = []
                with DDGS(timeout=20) as ddgs:
                    for r in ddgs.text(query, max_results=max_results, backend=backend):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("href", ""),
                            "snippet": r.get("body", ""),
                        })
                if results:
                    return results
                print(f"[web_search] Backend '{backend}' returned no results for: {query}")
            except Exception as e:
                print(f"[web_search] Backend '{backend}' attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(3 * attempt)

    print(f"[web_search] All backends failed for query: {query}")
    return []
