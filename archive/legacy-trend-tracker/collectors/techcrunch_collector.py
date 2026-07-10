"""
TechCrunch Collector — Fetches recent AI/startup news via RSS 2.0 feed.
Source: https://techcrunch.com/feed/ (RSS 2.0 format)
"""
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from typing import List, Dict, Optional


TCRUNCH_RSS = 'https://techcrunch.com/feed/'

# Keywords to filter for AI-relevant articles
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt',
    'agent', 'robot', 'autonomous', 'chip', 'gpu', 'nvidia', 'openai',
    'anthropic', 'deepmind', 'gemini', 'copilot', 'coding', 'inference',
    'data center', 'funding', 'series', 'raised', 'valuation', 'ipo',
    'startup', 'venture', 'generative', 'model', 'compute', 'cloud',
    'infrastructure', 'developer', 'software', 'api'
]


def _clean_text(text: Optional[str]) -> str:
    if not text:
        return ''
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return ' '.join(text.replace('\n', ' ').split())


def _is_ai_relevant(title: str, description: str) -> bool:
    text = (title + ' ' + description).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _classify_event_type(title: str, description: str) -> str:
    text = (title + ' ' + description).lower()
    if any(w in text for w in ['raises', 'raised', 'funding', 'series ', 'valuation', 'ipo', 'invests']):
        return 'FUNDING_ROUND'
    if any(w in text for w in ['launches', 'launched', 'releases', 'announces', 'unveils']):
        return 'PRODUCT_LAUNCH'
    if any(w in text for w in ['partners', 'partnership', 'collaboration', 'integrates']):
        return 'PARTNERSHIP'
    return 'PRODUCT_BETA'


def _parse_rss_date(date_str: str) -> str:
    """Parse RSS pubDate to YYYY-MM-DD."""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')


def fetch_recent_articles() -> List[Dict]:
    """Fetch recent TechCrunch articles filtered for AI relevance."""
    try:
        req = urllib.request.Request(TCRUNCH_RSS, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8')
    except Exception as e:
        print(f"  [TechCrunch] Fetch error: {e}")
        return []

    root = ET.fromstring(data)
    channel = root.find('channel')
    if channel is None:
        print("  [TechCrunch] No channel element found")
        return []

    events = []
    for item in channel.findall('item'):
        title_elem = item.find('title')
        desc_elem = item.find('description')
        link_elem = item.find('link')
        pubdate_elem = item.find('pubDate')

        title = _clean_text(title_elem.text if title_elem is not None else '')
        description = _clean_text(desc_elem.text if desc_elem is not None else '')
        url = link_elem.text if link_elem is not None else ''
        pub_date = _parse_rss_date(pubdate_elem.text) if pubdate_elem is not None else datetime.now().strftime('%Y-%m-%d')

        if not title or not _is_ai_relevant(title, description):
            continue

        event_type = _classify_event_type(title, description)

        events.append({
            'source_tier': 'P1',
            'source_name': 'TechCrunch',
            'event_type': event_type,
            'title': title[:200],
            'description': description[:500],
            'url': url,
            'published_date': pub_date,
            'amount_usd': None,
            'company_name': None,
            'raw_content': description[:800],
        })

    print(f"  [TechCrunch] Fetched {len(events)} AI-relevant articles")
    return events


if __name__ == '__main__':
    articles = fetch_recent_articles()
    for i, a in enumerate(articles[:5]):
        print(f"  {i+1}. [{a['published_date']}] [{a['event_type']}] {a['title'][:80]}...")
