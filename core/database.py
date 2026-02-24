import aiosqlite
from pathlib import Path

DB_PATH = Path("db/financial.db")


CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS raw_articles (
    id TEXT PRIMARY KEY,
    source TEXT,
    url TEXT,
    url_hash TEXT UNIQUE,
    title TEXT,
    published_at TEXT,
    raw_text TEXT,
    full_text TEXT,
    authors TEXT,
    top_image TEXT,
    meta_description TEXT,
    summary TEXT,
    scraped_at TEXT,
    status TEXT
);

CREATE INDEX IF NOT EXISTS idx_url_hash ON raw_articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_status ON raw_articles(status);
"""


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


async def article_exists(db, url_hash: str) -> bool:
    cursor = await db.execute(
        "SELECT 1 FROM raw_articles WHERE url_hash = ?",
        (url_hash,),
    )
    row = await cursor.fetchone()
    return row is not None


async def insert_article(db, article: dict):
    await db.execute(
        """
        INSERT INTO raw_articles
        (id, source, url, url_hash, title, published_at,
         raw_text, full_text, authors, top_image, meta_description, summary, scraped_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article["id"],
            article["source"],
            article["url"],
            article["url_hash"],
            article["title"],
            article["published_at"],
            article["raw_text"],
            article["full_text"],
            article["authors"],
            article["top_image"],
            article["meta_description"],
            article["summary"],
            article["scraped_at"],
            "scraped",
        ),
    )
    await db.commit()