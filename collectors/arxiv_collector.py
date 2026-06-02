"""
ArXiv Collector — Fetches recent AI/ML papers via arXiv API.
Categories: cs.AI, cs.CL, cs.LG, cs.CV, cs.RO
Free, no API key required. Rate limit: ~1 req/3s.
"""
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional


ARXIV_API = 'https://export.arxiv.org/api/query'
ARXIV_DELAY = 5  # seconds between requests to respect rate limit
CATEGORIES = ['cs.AI', 'cs.CL', 'cs.LG', 'cs.CV', 'cs.RO']
MAX_RESULTS = 5   # Minimal to reduce rate limit impact


def _clean_text(text: Optional[str]) -> str:
    if not text:
        return ''
    return ' '.join(text.replace('\n', ' ').split())


def fetch_recent_papers(days_back: int = 7) -> List[Dict]:
    """
    Fetch recent AI/ML papers from arXiv.
    Returns list of event dicts compatible with the Trend Tracker event schema.
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    # arXiv date format: YYYYMMDD
    date_range = f"[{start_date.strftime('%Y%m%d')}+TO+{end_date.strftime('%Y%m%d')}]"

    cat_query = '+OR+'.join([f'cat:{c}' for c in CATEGORIES])
    query = f'({cat_query})+AND+{date_range}'
    params = {
        'search_query': query,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending',
        'max_results': MAX_RESULTS
    }
    url = f'{ARXIV_API}?{urllib.parse.urlencode(params)}'

    # Respect arXiv rate limit
    time.sleep(ARXIV_DELAY)

    # Retry with backoff for rate limiting
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TrendTracker/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = (attempt + 1) * 5
                print(f"  [arXiv] Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [arXiv] HTTP error: {e}")
                return []
        except Exception as e:
            print(f"  [arXiv] Fetch error: {e}")
            return []

    root = ET.fromstring(data)
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }

    events = []
    for entry in root.findall('atom:entry', ns):
        title = _clean_text(entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else '')
        summary = _clean_text(entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else '')
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1] if entry.find('atom:id', ns) is not None else ''
        published = entry.find('atom:published', ns).text[:10] if entry.find('atom:published', ns) is not None else ''
        link = f'https://arxiv.org/abs/{arxiv_id}'

        # Determine categories for theme mapping hints
        cats = [c.get('term', '') for c in entry.findall('atom:category', ns)]
        cat_hint = ','.join(cats[:2]) if cats else ''

        events.append({
            'source_tier': 'P0',
            'source_name': 'arXiv',
            'event_type': 'RESEARCH_PAPER',
            'title': title[:200],
            'description': summary[:500],
            'url': link,
            'published_date': published,
            'amount_usd': None,
            'company_name': None,
            'raw_content': summary[:1000],
            'cat_hint': cat_hint  # used by theme mapper
        })

    print(f"  [arXiv] Fetched {len(events)} papers (last {days_back} days)")
    return events


if __name__ == '__main__':
    papers = fetch_recent_papers(7)
    for i, p in enumerate(papers[:5]):
        print(f"  {i+1}. [{p['published_date']}] {p['title'][:80]}... ({p['cat_hint']})")
