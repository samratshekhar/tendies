import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is on sys.path so package imports work
# when running the script directly (e.g. `python workflows/scrape.py`).
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import asyncio
import json
import typer
from rich import print
import aiosqlite

from core.database import init_db, article_exists, insert_article
from core.rss_client import parse_feed

app = typer.Typer()

CONFIG_PATH = Path("config/sources.json")


@app.command()
def main():
    asyncio.run(scrape_rss())


async def scrape_rss():
    start = datetime.now(timezone.utc).isoformat()
    print(f"[bold green]Initializing at {start}[/bold green]")
    await init_db()

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    async with aiosqlite.connect("db/financial.db") as db:

        total_inserted = 0

        for source in config["sources"]:
            if source["type"] != "rss":
                continue

            print(f"[blue]Fetching start {source['name']}[/blue]")

            # Parse the feed using the open database connection so that
            # `parse_feed` can check for existing url hashes before
            # enriching or collecting an article.
            articles = await parse_feed(db, source["url"], source["name"])

            for article in articles:
                # if not await article_exists(db, article["url_hash"]):
                await insert_article(db, article)
                total_inserted += 1
        end = datetime.now(timezone.utc).isoformat()
        runtime = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
        print(f"[bold yellow]Inserted {total_inserted} new articles at {end} with a runtime of {runtime:.2f} seconds.[/bold yellow]")


if __name__ == "__main__":
    app()