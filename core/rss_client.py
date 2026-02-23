import feedparser
import hashlib
import uuid
from datetime import datetime, timezone
from dateutil import parser as date_parser


def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def parse_feed(feed_url: str, source_name: str):
    feed = feedparser.parse(feed_url)

    articles = []

    for entry in feed.entries:
        url = entry.get("link")
        if not url:
            continue

        published = entry.get("published", "")
        try:
            published_dt = date_parser.parse(published)
        except Exception:
            published_dt = datetime.now(timezone.utc)

        article = {
            "id": str(uuid.uuid4()),
            "source": source_name,
            "url": url,
            "url_hash": hash_url(url),
            "title": entry.get("title", ""),
            "published_at": published_dt.isoformat(),
            "raw_text": entry.get("summary", ""),
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        articles.append(article)

    return articles