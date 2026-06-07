import logging
import random
import re
from datetime import datetime
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

AMAZON_BASE_URL = "https://www.amazon.de"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class AmazonScraper(BaseScraper):
    """Amazon product scraper with rotating user-agents.

    Note: Amazon actively blocks scraping. This is a best-effort implementation.
    For production use, consider the Amazon Product Advertising API.
    """

    def _get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        url = f"{AMAZON_BASE_URL}/s?k={quote(query)}&i=toys"
        prices: list[ScrapedPrice] = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        logger.warning("Amazon returned status %d", resp.status)
                        return prices
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            results = soup.select('[data-component-type="s-search-result"]')

            for result in results[:10]:
                try:
                    price_whole = result.select_one(".a-price-whole")
                    price_frac = result.select_one(".a-price-fraction")
                    if not price_whole:
                        continue

                    whole = price_whole.get_text(strip=True).replace(".", "").replace(",", "")
                    frac = price_frac.get_text(strip=True) if price_frac else "00"
                    price_val = float(f"{whole}.{frac}")

                    link_el = result.select_one("a.a-link-normal.s-no-outline")
                    href = link_el.get("href", "") if link_el else ""
                    full_url = f"{AMAZON_BASE_URL}{href}" if href.startswith("/") else href

                    title_el = result.select_one("h2 span")
                    seller_name = title_el.get_text(strip=True)[:100] if title_el else ""

                    prices.append(ScrapedPrice(
                        marketplace="amazon",
                        price=price_val,
                        currency="EUR",
                        condition="new",
                        seller=seller_name,
                        url=full_url,
                        scraped_at=datetime.utcnow(),
                    ))
                except (ValueError, AttributeError) as e:
                    logger.debug("Failed to parse Amazon result: %s", e)
                    continue

        except aiohttp.ClientError as e:
            logger.error("Amazon request failed: %s", e)
        except Exception as e:
            logger.error("Amazon scraping error: %s", e)

        return prices

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        return await self.search(product_name)

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Scrape price directly from an Amazon product page (ASIN-based URL)."""
        # Extract ASIN from URL (e.g. /dp/B0CXXXXXX or /gp/product/B0CXXXXXX)
        match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
        asin = match.group(1) if match else None
        product_url = f"{AMAZON_BASE_URL}/dp/{asin}" if asin else url

        prices: list[ScrapedPrice] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    product_url,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        logger.warning("Amazon product page returned %d", resp.status)
                        return prices
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            # Try multiple price selectors on the product detail page
            price_el = (
                soup.select_one("#priceblock_ourprice")
                or soup.select_one("#priceblock_dealprice")
                or soup.select_one(".a-price .a-offscreen")
                or soup.select_one("#corePrice_feature_div .a-offscreen")
            )

            if price_el:
                price_text = price_el.get_text(strip=True)
                # Parse German price format: "123,45 €" or "€123.45"
                price_text = price_text.replace("€", "").replace("\xa0", "").strip()
                price_text = price_text.replace(".", "").replace(",", ".")
                price_val = float(price_text)

                title_el = soup.select_one("#productTitle")
                title = title_el.get_text(strip=True)[:100] if title_el else ""

                prices.append(ScrapedPrice(
                    marketplace="amazon",
                    price=price_val,
                    currency="EUR",
                    condition="new",
                    seller=title,
                    url=product_url,
                    scraped_at=datetime.utcnow(),
                ))
        except (ValueError, AttributeError) as e:
            logger.debug("Failed to parse Amazon product page: %s", e)
        except aiohttp.ClientError as e:
            logger.error("Amazon product page request failed: %s", e)
        except Exception as e:
            logger.error("Amazon product page scraping error: %s", e)

        return prices


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = AmazonScraper()
        results = await scraper.search("Pokemon 151 Booster Box")
        for r in results:
            print(f"  {r.price} {r.currency} - {r.seller[:50]}")

    asyncio.run(main())
