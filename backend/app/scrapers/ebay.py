import logging
import re
from datetime import datetime
from base64 import b64encode

import aiohttp

from app.config import get_settings
from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

EBAY_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_ITEM_URL = "https://api.ebay.com/buy/browse/v1/item"


class EbayScraper(BaseScraper):
    """eBay Browse API scraper for sealed TCG products.

    Uses OAuth 2.0 Client Credentials flow.
    """

    def __init__(self):
        self.settings = get_settings()
        self._access_token: str | None = None

    async def _get_access_token(self) -> str | None:
        if self._access_token:
            return self._access_token

        client_id = self.settings.ebay_client_id
        client_secret = self.settings.ebay_client_secret
        if not client_id or not client_secret:
            logger.warning("eBay API credentials not configured")
            return None

        credentials = b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(EBAY_AUTH_URL, headers=headers, data=data) as resp:
                    if resp.status != 200:
                        logger.error("eBay auth failed: %d", resp.status)
                        return None
                    body = await resp.json()
                    self._access_token = body.get("access_token")
                    return self._access_token
        except aiohttp.ClientError as e:
            logger.error("eBay auth request failed: %s", e)
            return None

    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        token = await self._get_access_token()
        if not token:
            return []

        category_id = "183454"  # Sealed Trading Card Packs/Boxes
        params = {
            "q": query,
            "category_ids": category_id,
            "filter": "conditionIds:{1000}",  # New
            "sort": "price",
            "limit": "10",
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
            "Content-Type": "application/json",
        }

        prices: list[ScrapedPrice] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(EBAY_BROWSE_URL, headers=headers, params=params,
                                       timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.warning("eBay Browse API returned %d", resp.status)
                        return prices
                    data = await resp.json()

            for item in data.get("itemSummaries", []):
                try:
                    price_val = float(item["price"]["value"])
                    currency = item["price"].get("currency", "EUR")
                    prices.append(ScrapedPrice(
                        marketplace="ebay",
                        price=price_val,
                        currency=currency,
                        condition=item.get("condition", "New"),
                        seller=item.get("seller", {}).get("username", ""),
                        url=item.get("itemWebUrl", ""),
                        scraped_at=datetime.utcnow(),
                    ))
                except (KeyError, ValueError) as e:
                    logger.debug("Failed to parse eBay item: %s", e)
                    continue

        except aiohttp.ClientError as e:
            logger.error("eBay request failed: %s", e)

        return prices

    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        tcg = kwargs.get("tcg", "")
        return await self.search(f"{product_name} sealed", tcg)

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Get price for a specific eBay item by URL, extracting item ID."""
        # Extract item ID from eBay URL (e.g. /itm/123456789)
        match = re.search(r"/itm/(\d+)", url)
        if not match:
            logger.warning("Could not extract eBay item ID from URL: %s", url)
            return []

        item_id = match.group(1)
        token = await self._get_access_token()
        if not token:
            return []

        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
        }
        api_url = f"{EBAY_ITEM_URL}/v1|{item_id}|0"

        prices: list[ScrapedPrice] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers,
                                       timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.warning("eBay item API returned %d for %s", resp.status, item_id)
                        return prices
                    data = await resp.json()

            price_info = data.get("price", {})
            price_val = float(price_info.get("value", 0))
            if price_val > 0:
                prices.append(ScrapedPrice(
                    marketplace="ebay",
                    price=price_val,
                    currency=price_info.get("currency", "EUR"),
                    condition=data.get("condition", "New"),
                    seller=data.get("seller", {}).get("username", ""),
                    url=data.get("itemWebUrl", url),
                    scraped_at=datetime.utcnow(),
                ))
        except (aiohttp.ClientError, KeyError, ValueError) as e:
            logger.error("eBay item fetch failed: %s", e)

        return prices


if __name__ == "__main__":
    import asyncio

    async def main():
        scraper = EbayScraper()
        results = await scraper.search("Pokemon 151 Booster Box sealed")
        for r in results:
            print(f"  {r.price} {r.currency} - {r.seller}")

    asyncio.run(main())
