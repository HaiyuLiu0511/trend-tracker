"""
GitHub Collector — Fetches trending AI/ML repositories via GitHub API.
Uses GitHub Search API (free, no key for limited requests).
"""
import urllib.request
import json
from datetime import datetime, timedelta
from typing import List, Dict


GITHUB_API = 'https://api.github.com'

# Search queries for AI topics
SEARCH_QUERIES = [
    'topic:llm+pushed:>2026-05-25',
    'topic:ai-agent+pushed:>2026-05-25',
    'topic:generative-ai+pushed:>2026-05-25',
    'topic:robotics+pushed:>2026-05-25',
    'topic:machine-learning+language:python+pushed:>2026-05-25',
]


def fetch_trending_repos() -> List[Dict]:
    """Fetch trending AI repos via GitHub Search API."""
    # Dynamic date range: last 7 days
    date_threshold = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    events = []

    for query in SEARCH_QUERIES:
        q = query.replace('2026-05-25', date_threshold)
        url = f'{GITHUB_API}/search/repositories?q={q}&sort=stars&order=desc&per_page=10'
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'TrendTracker/1.0',
                'Accept': 'application/vnd.github.v3+json'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"  [GitHub] Fetch error for '{query[:30]}...': {e}")
            continue

        for repo in data.get('items', []):
            events.append({
                'source_tier': 'P1',
                'source_name': 'GitHub',
                'event_type': 'PRODUCT_BETA',
                'title': f"{repo['full_name']}: {repo.get('description', '')[:100]}",
                'description': f"Stars: {repo['stargazers_count']}, Language: {repo.get('language', 'N/A')}, Topics: {','.join(repo.get('topics', []))}",
                'url': repo['html_url'],
                'published_date': repo.get('pushed_at', '')[:10] or datetime.now().strftime('%Y-%m-%d'),
                'amount_usd': None,
                'company_name': repo['full_name'].split('/')[0],
                'raw_content': repo.get('description', '')[:500],
                'stars': repo.get('stargazers_count', 0),
                'topics': repo.get('topics', []),
            })

    # Deduplicate by URL
    seen = set()
    unique = []
    for e in events:
        if e['url'] not in seen:
            seen.add(e['url'])
            unique.append(e)

    print(f"  [GitHub] Fetched {len(unique)} unique repos")
    return unique


if __name__ == '__main__':
    repos = fetch_trending_repos()
    for i, r in enumerate(repos[:5]):
        print(f"  {i+1}. [{r['published_date']}] {r['title'][:80]}...")
