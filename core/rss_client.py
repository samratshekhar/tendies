import feedparser
import hashlib
import uuid
from datetime import datetime, timezone
from dateutil import parser as date_parser
import nltk
from newspaper import Article, Config
from core.database import article_exists

nltk.download('punkt_tab')
browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
request_timeout = 10 # seconds

def enrich_from_url(url: str):
    try:
        # Define a user agent that mimics a web browser
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'

        # Configure the settings
        config = Config()
        config.browser_user_agent = browser_user_agent
        config.request_timeout = request_timeout

        article = Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        return_obj = {
            "full_text": article.text,
            "authors": ",".join(article.authors) if article.authors else "",
            "top_image": article.top_image,
            "meta_description": article.meta_description,
            "keywords": article.keywords,
            "summary": article.summary,
        }
        # print(f"Enriched {url} with metadata: {return_obj}")
        return return_obj
    except Exception as e:
        print(f"Failed to enrich {url}: {e}")
        return {}

def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def parse_feed(db, feed_url: str, source_name: str):
    """Fetch entries from an RSS feed, skip any already-present articles.

    The database connection must be supplied so we can query for existing
    URL hashes before doing expensive enrichment work. This function is now
    asynchronous because it awaits `article_exists` in the loop.
    """
    articles = []
    scraped_at = datetime.now(timezone.utc).isoformat()
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        url = entry.get("link")
        if not url:
            continue
        
        url_hash = hash_url(url)
        # short-circuit if we've already seen this article
        if await article_exists(db, url_hash):
            continue
        
        published = entry.get("published", "")
        try:
            published_dt = date_parser.parse(published)
        except Exception:
            published_dt = datetime.now(timezone.utc)

        # enrichment is relatively expensive, so only do it after the existence
        # check above
        enrichment = enrich_from_url(url)
        article = {
            "id": str(uuid.uuid4()),
            "source": source_name,
            "url": url,
            "url_hash": url_hash,
            "title": entry.get("title", ""),
            "published_at": published_dt.isoformat(),
            "raw_text": entry.get("summary", ""),
            "full_text": enrichment.get("full_text", ""),
            "authors": enrichment.get("authors", ""),
            "top_image": enrichment.get("top_image", ""),
            "meta_description": enrichment.get("meta_description", ""),
            "summary": enrichment.get("summary", ""),
            "scraped_at": scraped_at,
        }
        # print(f"Parsed article: {article['title']} from {source_name}")
        articles.append(article)

    return articles