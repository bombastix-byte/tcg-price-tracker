import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

_PW_FETCH_SCRIPT = str(Path(__file__).parent / "_pw_fetch.py")


class IdealoScraper(BaseScraper):
    """Idealo.de price comparison scraper using Playwright with real Chrome."""

    async def _fetch_page(self, url: str) -> str | None:
        """Fetch Idealo page via Playwright subprocess with Chrome channel."""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    sys.executable, _PW_FETCH_SCRIPT, url,
                    ".productOffers-listItemOfferPrice", "20000",
                    "--use-chrome",
                ],
                capture_output=True,
                text=True,
                timeout=90,
            )
            if result.returncode != 0:
                logger.error("Idealo Playwright failed: %s", result.stderr[:500])
                return None
            data = json.loads(result.stdout)
            if "error" in data:
                logger.error("Idealo fetch error: %s", data["error"])
                return None
            return data["html"]
        except Exception as e:
            logger.error("Idealo fetch failed for %s: %s", url, e)
            return None

    def _parse_price_text(self, text: str) -> float | None:
        """Parse German price format: '120,31 €' or '1.234,56 €'."""
        try:
            cleaned = text.replace("€", "").replace("\xa0", "").strip()
            cleaned = cleaned.replace(".", "").replace(",", ".")
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def _parse_product_page(self, html: str, url: str) -> list[ScrapedPrice]:
        """Extract best price from Idealo offer list."""
        from bs4 import BeautifulSoup

        prices: list[ScrapedPrice] = []
        soup = BeautifulSoup(html, "html.parser")

        price_elements = soup.select(".productOffers-listItemOfferPrice")
        best_price: float | None = None

        for el in price_elements:
            val = self._parse_price_text(el.get_text(strip=True))
            if val is not None and (best_price is None or val < best_price):
                best_price = val

        if best_price is not None:
            prices.append(ScrapedPrice(
                marketplace="idealo",
                price=best_price,
                currency="EUR",
                condition="new",
                seller="Idealo (best price)",
                url=url,
                scraped_at=datetime.now(tz=None),
            ))

        return prices

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Scrape price directly from an Idealo product page."""
        html = await self._fetch_page(url)
        if html is None:
            return []
        return self._parse_product_page(html, url)

    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        """Search not supported. Use marketplace links."""
        logger.warning("Idealo search not supported. Use marketplace links.")
        return []

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        return await self.search(product_name)


if __name__ == "__main__":

    async def main():
        scraper = IdealoScraper()
        results = await scraper.get_price_by_url(
            "https://www.idealo.de/preisvergleich/OffersOfProduct/203791818_-pokemon-karmesin-purpur-prismatische-entwicklungen-booster-bundle-pokemon.html"
        )
        for r in results:
            print(f"  {r.price} {r.currency} - {r.seller} - {r.url}")

    asyncio.run(main())
