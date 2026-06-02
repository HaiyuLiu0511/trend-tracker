"""
Reuters Collector — Fetches AI/tech news via WebSearch.
Reuters has no free public RSS for tech; we use WebSearch as proxy.

NOTE: This collector requires the WebSearch tool (not urllib).
In the pipeline context, this is a placeholder — the actual search happens
in the pipeline script via the WebSearch function.
"""
from typing import List, Dict


REUTERS_QUERIES = [
    'Reuters AI artificial intelligence funding investment 2026',
    'Reuters Nvidia chip semiconductor data center',
    'Reuters AI startup funding round valuation',
    'Reuters robotics humanoid automation'
]


def build_search_queries() -> List[str]:
    """Return search queries for Reuters AI/tech news."""
    return REUTERS_QUERIES


if __name__ == '__main__':
    for q in REUTERS_QUERIES:
        print(f"  Query: {q}")
