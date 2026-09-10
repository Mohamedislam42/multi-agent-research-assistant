"""
Multi-Agent Research Assistant — CLI entry point.

Usage:
    python main.py "your research question here"

Produces a Markdown report (report.md) synthesized and fact-checked
across multiple collaborating agents.
"""

import os
import sys

from agents.coordinator import Coordinator


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "your research question"')
        sys.exit(1)

    if not os.environ.get("GROQ_API_KEY"):
        print("Set your GROQ_API_KEY environment variable first.")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    coordinator = Coordinator()
    report = coordinator.run(question)

    output_path = "report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nDone. Report saved to {output_path}\n")
    print(report)


if __name__ == "__main__":
    main()
