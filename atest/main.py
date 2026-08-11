#!/usr/bin/env python3
"""Entry point of the relevance audit suite. Use for debug."""

import os
import sys
from pathlib import Path

from robot import run_cli

ATEST = Path(__file__).resolve().parent
SUITE = ATEST / "tests" / "relevance.robot"
MODIFIER = ATEST / "libs" / "TestCaseGenerator.py"
RESULTS = ATEST / "results"
AGENT_ID = os.environ.get("AGENT_ID")


def main(argv: list[str] | None = None) -> int:
    """Run the suite and return the Robot Framework return code."""
    arguments = [
        "--prerunmodifier",
        str(MODIFIER),
        "--outputdir",
        str(RESULTS),
        "--debugfile",
        "debug.txt",
        "--variable",
        f"AGENT_ID:{AGENT_ID}",
        "--loglevel",
        "DEBUG",
        "--include",
        "resource:communautes-le-metier-du-test",
        *(sys.argv[1:] if argv is None else argv),
        str(SUITE),
    ]
    return run_cli(arguments, exit=False)


if __name__ == "__main__":
    sys.exit(main())
