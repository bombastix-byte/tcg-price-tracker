import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Product, Price
from app.schemas import PriceOut, PriceHistoryPoint
from app.services.price_service import update_prices_for_product, get_price_history

router = APIRouter()

# Base prices for demo data (by category)
_DEMO_BASE_PRICES = {
    "booster_box": {"cardmarket": 135.0, "ebay": 142.0, "amazon": 149.99},
    "etb": {"cardmarket": 42.0, "ebay": 45.0, "amazon": 49.99},
    "blister": {"cardmarket": 28.0, "ebay": 32.0, "amazon": 34.99},
    "collection_box": {"cardmarket": 95.0, "ebay": 105.0, "amazon": 119.99},
    "bundle": {"cardmarket": 32.0, "ebay": 36.0, "amazon": 39.99},
    "booster_pack": {"cardmarket": 4.0, "ebay": 4.50, "amazon": 5.49},
    "other": {"cardmarket": 25.0, "ebay": 28.0, "amazon": 32.99},
}


async def _seed_demo_prices(db: AsyncSession, product: Product) -> list[Price]:
    """Generate realistic demo price data with 14 days of history."""
    base = _DEMO_BASE_PRICES.get(product.category, _DEMO_BASE_PRICES["other"])
    prices: list[Price] = []
    now = datetime.utcnow()

    for day_offset in range(14, -1, -1):
        ts = now - timedelta(days=day_offset)
        for mp, base_price in base.items():
            # Add some daily variation (+/- 8%)
            variation = random.uniform(-0.08, 0.08)
            price_val = round(base_price * (1 + variation), 2)
            p = Price(
                product_id=product.id,
                marketplace=mp,
                price=price_val,
                currency="EUR",
                condition="new",
                seller=f"Demo {mp.title()} Seller",
                url=f"https://{mp}.example.com/product/{product.id}",
                scraped_at=ts,
            )
            db.add(p)
            prices.append(p)

    await db.commit()
    return prices


@router.get("/products/{product_id}/prices", response_model=list[PriceOut])
async def get_current_prices(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get the most recent prices for a product from all marketplaces."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    result = await db.execute(
        select(Price)
        .where(Price.product_id == product_id)
        .order_by(Price.scraped_at.desc())
        .limit(30)
    )
    return result.scalars().all()


@router.post("/products/{product_id}/prices/refresh", response_model=list[PriceOut])
async def refresh_prices(product_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger a fresh price fetch for a product. Falls back to demo data if scrapers fail."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = await update_prices_for_product(db, product_id)

    # If all scrapers returned empty (no API keys / blocked), seed demo data
    if not prices:
        prices = await _seed_demo_prices(db, product)

    return prices


@router.get("/products/{product_id}/history", response_model=list[PriceHistoryPoint])
async def get_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get price history (lowest price per marketplace per day)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    history = await get_price_history(db, product_id, days)
    return history


@router.post("/seed-demo", response_model=dict)
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Seed demo price data for all products (dev/demo only)."""
    result = await db.execute(select(Product))
    products = result.scalars().all()
    total = 0
    for product in products:
        # Skip if product already has prices from all 3 marketplaces
        existing = await db.execute(
            select(Price).where(Price.product_id == product.id).limit(1)
        )
        if existing.scalar_one_or_none():
            # Delete old prices first for a clean demo
            from sqlalchemy import delete
            await db.execute(delete(Price).where(Price.product_id == product.id))
            await db.commit()

        prices = await _seed_demo_prices(db, product)
        total += len(prices)
    return {"message": f"Seeded {total} demo prices for {len(products)} products"}
