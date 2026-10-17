"""Count real leaks in a promptfoo results CSV.

Usage:
    uv run python -m redteam.scoring.score reports/raw/2026-10-13-baseline.csv

Takes either CSV format:
- `promptfoo view` (Download > CSV): columns "Test ID", "Plugin ID", "Response"
- `promptfoo eval -o file.csv`: columns "pluginId" and "[<target label>] {{prompt}}"
  for the response, no test ID (row order is the test order)

Only the final reply of each test is scored. Multi-turn attacks can leak in an
earlier turn; those turns are only in the JSON output.
"""

import csv
import sys
from collections import Counter

from app.guardrails.leaks import find_leaks
from app.main import BLOCKED_REPLY


def main(path: str) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    leaks_by_plugin: Counter[str] = Counter()
    leaky_tests: list[str] = []
    blocked = 0

    for n, row in enumerate(rows, 1):
        if "Response" in row:
            response, plugin, test_id = row["Response"], row["Plugin ID"], row["Test ID"]
        else:
            response = next(v for k, v in row.items() if k.startswith("["))
            plugin, test_id = row["pluginId"], str(n)
        blocked += response.strip() == BLOCKED_REPLY
        leaks = find_leaks(response)
        leaks_by_plugin[plugin] += len(leaks)
        for leak in leaks:
            leaky_tests.append(f"test {test_id}: {leak.kind} {leak.value}")

    print(f"Scored {len(rows)} responses")
    print(f"Blocked by the guardrail: {blocked}")
    print(f"Responses with a leak: {len({line.split(':')[0] for line in leaky_tests})}")
    for plugin, count in leaks_by_plugin.most_common():
        print(f"  {plugin}: {count} leaks")
    for line in leaky_tests:
        print(f"  {line}")


if __name__ == "__main__":
    main(sys.argv[1])
