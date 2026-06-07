import logging
from datetime import datetime
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

from app.config import get_settings
from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

CARDMARKET_BASE_URL = "https://www.cardmarket.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class CardmarketScraper(BaseScraper):
    """Scraper for Cardmarket sealed products.

    Uses web scraping as primary method.
    Cardmarket API (OAuth 1.0) can be integrated when credentials are available.
    """

    def __init__(self):
        self.settings = get_settings()
        self.headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}

    async def search(self, query: str, tcg: str = "pokemon") -> list[ScrapedPrice]:
        game = "Pokemon" if tcg == "pokemon" else "MagicTheGathering"
        search_url = (
            f"{CARDMARKET_BASE_URL}/en/{game}/Products/Search"
            f"?searchString={quote(query)}&mode=gallery"
        )
        return await self._scrape_search_page(search_url)

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        tcg = kwargs.get("tcg", "pokemon")
        return await self.search(product_name, tcg)

    async def _scrape_search_page(self, url: str) -> list[ScrapedPrice]:
        prices: list[ScrapedPrice] = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.warning("Cardmarket returned status %d for %s", resp.status, url)
                        return prices
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            product_tiles = soup.select(".col-12.col-md-8.px-2.flex-column")

            if not product_tiles:
                product_tiles = soup.select("div.table-body .row")

            for tile in product_tiles[:10]:
                try:
                    name_el = tile.select_one("a")
                    price_el = tile.select_one(".price-container span, .col-price span")
                    if not name_el or not price_el:
                        continue

                    price_text = price_el.get_text(strip=True).replace("€", "").replace(",", ".").strip()
                    link = name_el.get("href", "")
                    full_url = f"{CARDMARKET_BASE_URL}{link}" if link.startswith("/") else link

                    prices.append(ScrapedPrice(
                        marketplace="cardmarket",
                        price=float(price_text),
                        currency="EUR",
                        condition="new",
                        seller="Cardmarket",
                        url=full_url,
                        scraped_at=datetime.utcnow(),
                    ))
                except (ValueError, AttributeError) as e:
                    logger.debug("Failed to parse Cardmarket tile: %s", e)
                    continue

        except aiohttp.ClientError as e:
            logger.error("Cardmarket request failed: %s", e)
        except Exception as e:
            logger.error("Cardmarket scraping error: %s", e)

        return prices

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Scrape price directly from a Cardmarket product page."""
        prices: list[ScrapedPrice] = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.warning("Cardmarket product page returned %d for %s", resp.status, url)
                        return prices
                    html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            # Try to find the "From" price on the product detail page
            price_el = soup.select_one(".info-list-container dd .font-weight-bold, .price-container .font-weight-bold")
            if not price_el:
                # Fallback: look for trend price
                price_el = soup.select_one(".price-container span")

            if price_el:
                price_text = price_el.get_text(strip=True).replace("€", "").replace(",", ".").strip()
                prices.append(ScrapedPrice(
                    marketplace="cardmarket",
                    price=float(price_text),
                    currency="EUR",
                    condition="new",
                    seller="Cardmarket",
                    url=url,
                    scraped_at=datetime.utcnow(),
                ))
        except (ValueError, AttributeError) as e:
            logger.debug("Failed to parse Cardmarket product page: %s", e)
        except aiohttp.ClientError as e:
            logger.error("Cardmarket product page request failed: %s", e)
        except Exception as e:
            logger.error("Cardmarket product page scraping error: %s", e)

        return prices


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = CardmarketScraper()
        results = await scraper.search("Pokemon 151 Booster Box", tcg="pokemon")
        for r in results:
            print(f"  {r.price} {r.currency} - {r.url}")

    asyncio.run(main())
