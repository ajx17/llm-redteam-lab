"""Count real leaks in a promptfoo results CSV.

Usage:
    uv run python -m redteam.scoring.score reports/raw/2026-10-13-baseline.csv

Export the CSV from `promptfoo view` (Download > CSV). It needs the columns
"Test ID", "Plugin ID", "Strategy" and "Response".
"""

import csv
import sys
from collections import Counter

from app.guardrails.leaks import find_leaks


def main(path: str) -> None:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))

    leaks_by_plugin: Counter[str] = Counter()
    leaky_tests: list[str] = []

    for row in rows:
        leaks = find_leaks(row["Response"])  # noqa: F841 (delete this comment in step 4)
        # TODO (step 4): if this row has any leaks:
        #   - add len(leaks) to leaks_by_plugin[row["Plugin ID"]]
        #   - append a line like "test 12: canary ACME-CANARY-7f3a9c" to leaky_tests
        #     (one line per leak)

    print(f"Scored {len(rows)} responses")
    print(f"Responses with a leak: {len({line.split(':')[0] for line in leaky_tests})}")
    for plugin, count in leaks_by_plugin.most_common():
        print(f"  {plugin}: {count} leaks")
    for line in leaky_tests:
        print(f"  {line}")


if __name__ == "__main__":
    main(sys.argv[1])
