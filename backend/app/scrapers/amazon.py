import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

AMAZON_BASE_URL = "https://www.amazon.de"
_PW_FETCH_SCRIPT = str(Path(__file__).parent / "_pw_fetch.py")


class AmazonScraper(BaseScraper):
    """Amazon.de product scraper using Playwright for reliable page loading."""

    async def _fetch_page(self, url: str) -> str | None:
        """Fetch Amazon page via Playwright subprocess."""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, _PW_FETCH_SCRIPT, url, "#productTitle", "15000"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.error("Amazon Playwright failed: %s", result.stderr[:500])
                return None
            data = json.loads(result.stdout)
            if "error" in data:
                logger.error("Amazon fetch error: %s", data["error"])
                return None
            return data["html"]
        except Exception as e:
            logger.error("Amazon fetch failed for %s: %s", url, e)
            return None

    def _parse_price_text(self, text: str) -> float | None:
        """Parse German price format: '120,31 €' or '1.234,56 €'."""
        try:
            cleaned = text.replace("€", "").replace("\xa0", "").strip()
            # German format: dots as thousands separator, comma as decimal
            cleaned = cleaned.replace(".", "").replace(",", ".")
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def _parse_product_page(self, html: str, url: str) -> list[ScrapedPrice]:
        """Extract price from an Amazon product detail page."""
        from bs4 import BeautifulSoup

        prices: list[ScrapedPrice] = []
        soup = BeautifulSoup(html, "html.parser")

        title_el = soup.select_one("#productTitle")
        title = title_el.get_text(strip=True)[:100] if title_el else ""

        # Try price selectors in order of specificity
        price_el = (
            soup.select_one("#corePrice_feature_div .a-offscreen")
            or soup.select_one("#corePriceDisplay_desktop_feature_div .a-offscreen")
            or soup.select_one(".a-price .a-offscreen")
            or soup.select_one("#priceblock_ourprice")
            or soup.select_one("#priceblock_dealprice")
        )

        if price_el:
            price_val = self._parse_price_text(price_el.get_text(strip=True))
            if price_val is not None:
                prices.append(ScrapedPrice(
                    marketplace="amazon",
                    price=price_val,
                    currency="EUR",
                    condition="new",
                    seller=title,
                    url=url,
                    scraped_at=datetime.now(tz=None),
                ))
        else:
            logger.warning("No price found on Amazon page: %s", url)

        return prices

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Scrape price directly from an Amazon product page."""
        html = await self._fetch_page(url)
        if html is None:
            return []
        return self._parse_product_page(html, url)

    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        """Search not reliable due to bot detection. Use marketplace links."""
        logger.warning("Amazon search not supported. Use marketplace links with ASINs.")
        return []

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        return await self.search(product_name)


if __name__ == "__main__":

    async def main():
        scraper = AmazonScraper()
        results = await scraper.get_price_by_url(
            "https://www.amazon.de/dp/B0D5PV25GL"
        )
        for r in results:
            print(f"  {r.price} {r.currency} - {r.seller} - {r.url}")

    asyncio.run(main())
