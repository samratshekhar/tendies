import sys
from pathlib import Path

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
    print("[bold green]Initializing database...[/bold green]")
    await init_db()

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    async with aiosqlite.connect("db/financial.db") as db:

        total_inserted = 0

        for source in config["sources"]:
            if source["type"] != "rss":
                continue

            print(f"[blue]Fetching {source['name']}[/blue]")

            articles = parse_feed(source["url"], source["name"])

            for article in articles:
                if not await article_exists(db, article["url_hash"]):
                    await insert_article(db, article)
                    total_inserted += 1

        print(f"[bold yellow]Inserted {total_inserted} new articles.[/bold yellow]")


if __name__ == "__main__":
    app()