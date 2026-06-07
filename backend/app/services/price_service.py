import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Product, Price, Marketplace, MarketplaceLink
from app.scrapers.cardmarket import CardmarketScraper
from app.scrapers.ebay import EbayScraper
from app.scrapers.amazon import AmazonScraper
from app.scrapers.base import BaseScraper, ScrapedPrice

logger = logging.getLogger(__name__)

MARKETPLACE_SCRAPERS: dict[str, type[BaseScraper]] = {
    "cardmarket": CardmarketScraper,
    "ebay": EbayScraper,
    "amazon": AmazonScraper,
}


async def fetch_prices_for_product(product: Product) -> list[ScrapedPrice]:
    """Fetch prices from all marketplaces for a product.

    If a MarketplaceLink exists for a marketplace, uses direct URL scraping.
    Otherwise falls back to name-based search.
    """
    # Build a lookup of marketplace -> link URL
    link_by_mp: dict[str, str] = {}
    for link in product.marketplace_links:
        if link.url:
            link_by_mp[link.marketplace] = link.url

    all_prices: list[ScrapedPrice] = []
    tasks = []

    for mp_name, scraper_cls in MARKETPLACE_SCRAPERS.items():
        scraper = scraper_cls()
        if mp_name in link_by_mp:
            tasks.append(scraper.get_price_by_url(link_by_mp[mp_name]))
        else:
            tasks.append(scraper.get_price(product.name, tcg=product.tcg))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logger.error("Scraper error: %s", result)
            continue
        all_prices.extend(result)

    return all_prices


async def update_prices_for_product(session: AsyncSession, product_id: int) -> list[Price]:
    """Fetch fresh prices and store them in the database."""
    result = await session.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.marketplace_links))
    )
    product = result.scalar_one_or_none()
    if not product:
        return []

    scraped = await fetch_prices_for_product(product)
    db_prices: list[Price] = []

    for sp in scraped:
        price = Price(
            product_id=product_id,
            marketplace=sp.marketplace,
            price=sp.price,
            currency=sp.currency,
            condition=sp.condition,
            seller=sp.seller,
            url=sp.url,
            scraped_at=sp.scraped_at,
        )
        session.add(price)
        db_prices.append(price)

    await session.commit()
    return db_prices


async def get_lowest_prices(session: AsyncSession, product_id: int) -> dict[str, float | None]:
    """Get the lowest current price per marketplace for a product."""
    lowest: dict[str, float | None] = {}
    for mp in Marketplace:
        result = await session.execute(
            select(Price)
            .where(Price.product_id == product_id, Price.marketplace == mp.value)
            .order_by(Price.scraped_at.desc(), Price.price.asc())
            .limit(1)
        )
        price = result.scalar_one_or_none()
        lowest[mp.value] = price.price if price else None

    return lowest


async def get_price_history(
    session: AsyncSession, product_id: int, days: int = 30
) -> list[dict]:
    """Get aggregated price history (lowest per marketplace per day)."""
    from datetime import timedelta
    from sqlalchemy import func

    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(
            func.date(Price.scraped_at).label("date"),
            Price.marketplace,
            func.min(Price.price).label("min_price"),
        )
        .where(Price.product_id == product_id, Price.scraped_at >= cutoff)
        .group_by(func.date(Price.scraped_at), Price.marketplace)
        .order_by(func.date(Price.scraped_at))
    )
    rows = result.all()

    history: dict[str, dict[str, float | None]] = {}
    for date_str, marketplace, min_price in rows:
        d = str(date_str)
        if d not in history:
            history[d] = {"date": d, "cardmarket": None, "ebay": None, "amazon": None}
        history[d][marketplace] = min_price

    return list(history.values())
