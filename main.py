"""
Multi-Agent Research Assistant — CLI entry point.

Usage:
    python main.py "your research question here"
    python main.py --model llama-3.1-8b-instant "your research question"

Produces a grounded, fact-checked Markdown report (report.md).
"""

import argparse
import os
import sys

# Load dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agents.coordinator import Coordinator, DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Autonomous Research Assistant")
    parser.add_argument("question", nargs="+", help="Research question or topic")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Groq LLM model (default: {DEFAULT_MODEL})")
    parser.add_argument("--subqueries", type=int, default=3, help="Number of subqueries to generate")
    parser.add_argument("--output", default="report.md", help="Output markdown report file")

    args = parser.parse_args()

    if not os.environ.get("GROQ_API_KEY"):
        print("Error: Set your GROQ_API_KEY environment variable first.")
        print("Example: export GROQ_API_KEY='gsk_...' or $env:GROQ_API_KEY='gsk_...'")
        sys.exit(1)

    question = " ".join(args.question)

    print("=" * 60)
    print("⚡ MULTI-AGENT AUTONOMOUS RESEARCH ASSISTANT")
    print("=" * 60)
    print(f"Topic: {question}")
    print(f"Model: {args.model}\n")

    coordinator = Coordinator(model=args.model)
    report = coordinator.run(question, num_queries=args.subqueries, return_details=False)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 60)
    print(f"✅ Research completed successfully! Report written to: {args.output}")
    print("=" * 60 + "\n")
    print(report)


if __name__ == "__main__":
    main()
