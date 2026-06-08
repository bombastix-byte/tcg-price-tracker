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


class CardmarketScraper(BaseScraper):
    """Scraper for Cardmarket sealed products using Playwright to bypass Cloudflare."""

    async def _fetch_page(self, url: str) -> str | None:
        """Fetch page via subprocess to avoid asyncio event loop conflicts."""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, _PW_FETCH_SCRIPT, url],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.error("Playwright subprocess failed: %s", result.stderr[:500])
                return None
            data = json.loads(result.stdout)
            if "error" in data:
                logger.error("Playwright fetch error: %s", data["error"])
                return None
            return data["html"]
        except Exception as e:
            logger.error("Cardmarket fetch failed for %s: %s", url, e)
            return None

    def _parse_price(self, text: str) -> float | None:
        """Parse a price string like '135,00 €' into a float."""
        try:
            cleaned = text.replace("€", "").replace("\xa0", "").replace(",", ".").strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def _parse_product_page(self, html: str, url: str) -> list[ScrapedPrice]:
        """Extract prices from a Cardmarket product detail page."""
        from bs4 import BeautifulSoup

        prices: list[ScrapedPrice] = []
        soup = BeautifulSoup(html, "html.parser")

        price_data: dict[str, float] = {}
        for dt in soup.select("dt"):
            label = dt.get_text(strip=True).lower()
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue
            val = self._parse_price(dd.get_text(strip=True))
            if val is None:
                continue

            if label == "from":
                price_data["from"] = val
            elif label == "price trend":
                price_data["trend"] = val
            elif "30-day" in label:
                price_data["avg30"] = val
            elif "7-day" in label:
                price_data["avg7"] = val
            elif "1-day" in label:
                price_data["avg1"] = val

        # Use "From" (lowest available) as the primary price
        primary = price_data.get("from") or price_data.get("trend")
        if primary is not None:
            prices.append(ScrapedPrice(
                marketplace="cardmarket",
                price=primary,
                currency="EUR",
                condition="sealed",
                seller="Cardmarket (lowest)",
                url=url,
                scraped_at=datetime.now(tz=None),
            ))

        # Also store trend price if different from "from"
        trend = price_data.get("trend")
        if trend is not None and trend != primary:
            prices.append(ScrapedPrice(
                marketplace="cardmarket",
                price=trend,
                currency="EUR",
                condition="sealed",
                seller="Cardmarket (trend)",
                url=url,
                scraped_at=datetime.now(tz=None),
            ))

        return prices

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Scrape price directly from a Cardmarket product page."""
        html = await self._fetch_page(url)
        if html is None:
            return []
        return self._parse_product_page(html, url)

    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        """Search not supported due to Cloudflare. Use marketplace links instead."""
        logger.warning("Cardmarket search not supported (Cloudflare). Use marketplace links.")
        return []

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        """Fallback: search not supported, use get_price_by_url with MarketplaceLinks."""
        return await self.search(product_name)


if __name__ == "__main__":

    async def main():
        scraper = CardmarketScraper()
        results = await scraper.get_price_by_url(
            "https://www.cardmarket.com/en/Pokemon/Products/Booster-Boxes/Pokemon-Card-151-Booster-Box"
        )
        for r in results:
            print(f"  {r.price} {r.currency} - {r.seller} - {r.url}")

    asyncio.run(main())
