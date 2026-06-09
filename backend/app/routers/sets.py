import json
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Product, TCG
from app.schemas import (
    SetSummary, SetDetail, TopCard, BoosterValue,
    ProductWithPrices, ProductOut, MarketplaceLinkOut, PriceHistoryPoint,
)
from app.services.set_service import (
    get_set_list, get_or_refresh_set_cache, get_booster_values, get_top_deals,
)
from app.services.price_service import get_lowest_prices, get_price_history

router = APIRouter()


@router.get("/", response_model=list[SetSummary])
async def list_sets(
    tcg: TCG | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all sets with product counts, optionally filtered by TCG."""
    return await get_set_list(db, tcg)


@router.get("/top-deals", response_model=list[BoosterValue])
async def top_deals(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get the cheapest booster deals across all sets."""
    deals = await get_top_deals(db, limit)
    return [
        BoosterValue(
            product=ProductOut.model_validate(d["product"]),
            lowest_price=d["lowest_price"],
            pack_count=d["pack_count"],
            price_per_pack=d["price_per_pack"],
            top_card_value=d["top_card_value"],
            value_score=d["value_score"],
        )
        for d in deals
    ]


@router.get("/{set_code}", response_model=SetDetail)
async def get_set_detail(set_code: str, db: AsyncSession = Depends(get_db)):
    """Get detailed set information including top cards, sealed products, and booster values."""
    # Find TCG for this set_code
    result = await db.execute(
        select(Product.tcg).where(Product.set_code.ilike(set_code)).limit(1)
    )
    tcg = result.scalar_one_or_none()
    if not tcg:
        raise HTTPException(status_code=404, detail="Set not found")

    # Get/refresh cached set info + top cards from external API
    cache = await get_or_refresh_set_cache(db, set_code, tcg)
    top_cards_data = json.loads(cache.top_cards_json)
    top_cards = [TopCard(**tc) for tc in top_cards_data]

    # Sum of top card values for value score
    top_card_value_sum = sum(tc.price_eur or 0 for tc in top_cards) or None

    # Get all sealed products for this set
    products_result = await db.execute(
        select(Product)
        .where(Product.set_code.ilike(set_code))
        .options(selectinload(Product.marketplace_links))
        .order_by(Product.name)
    )
    products = products_result.scalars().all()

    # Build ProductWithPrices for each
    sealed_products = []
    for p in products:
        lowest = await get_lowest_prices(db, p.id)
        sealed_products.append(ProductWithPrices(
            **{c.name: getattr(p, c.name) for c in Product.__table__.columns},
            lowest_prices=lowest,
            marketplace_links=[MarketplaceLinkOut.model_validate(l) for l in p.marketplace_links],
        ))

    # Booster values (sorted by price per pack)
    booster_vals = await get_booster_values(db, products, top_card_value_sum)
    booster_values = [
        BoosterValue(
            product=ProductOut.model_validate(bv["product"]),
            lowest_price=bv["lowest_price"],
            pack_count=bv["pack_count"],
            price_per_pack=bv["price_per_pack"],
            top_card_value=bv["top_card_value"],
            value_score=bv["value_score"],
        )
        for bv in booster_vals
    ]

    # Aggregate price trend across all products in the set
    trend_data: dict[str, dict[str, float | None]] = defaultdict(
        lambda: {"cardmarket": None, "ebay": None, "amazon": None, "idealo": None, "geizhals": None}
    )
    for p in products:
        hist = await get_price_history(db, p.id, days=90)
        for point in hist:
            d = point["date"]
            for mp in ["cardmarket", "ebay", "amazon", "idealo", "geizhals"]:
                val = point.get(mp)
                if val is not None:
                    current = trend_data[d].get(mp)
                    trend_data[d][mp] = (current or 0) + val

    price_trend = [
        PriceHistoryPoint(date=d, **v)
        for d, v in sorted(trend_data.items())
    ]

    return SetDetail(
        set_code=cache.set_code,
        tcg=cache.tcg,
        set_name=cache.set_name,
        release_date=cache.release_date,
        logo_url=cache.logo_url,
        symbol_url=cache.symbol_url,
        total_cards=cache.total_cards,
        top_cards=top_cards,
        sealed_products=sealed_products,
        booster_values=booster_values,
        price_trend=price_trend,
    )
