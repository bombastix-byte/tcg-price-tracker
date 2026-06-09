import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.models import SetCache, Product, Price, TCG, Marketplace
from app.services.price_service import get_lowest_prices, get_price_history

logger = logging.getLogger(__name__)

CACHE_TTL_HOURS = 24

CATEGORY_PACK_DEFAULTS = {
    "booster_box": 36,
    "etb": 8,
    "bundle": 6,
    "blister": 1,
    "booster_pack": 1,
    "collection_box": 4,
    "other": 1,
}


def effective_pack_count(product: Product) -> int:
    """Get the effective pack count for a product (explicit or category default)."""
    if product.pack_count:
        return product.pack_count
    return CATEGORY_PACK_DEFAULTS.get(product.category, 1)


# ---------------------------------------------------------------------------
# Pokemon TCG API (pokemontcg.io)
# ---------------------------------------------------------------------------

async def _fetch_pokemon_set(set_code: str) -> dict:
    """Fetch set metadata from pokemontcg.io."""
    settings = get_settings()
    headers = {}
    if settings.pokemon_tcg_api_key:
        headers["X-Api-Key"] = settings.pokemon_tcg_api_key

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.pokemontcg.io/v2/sets/{set_code}",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return {
            "set_name": data["name"],
            "release_date": data.get("releaseDate"),
            "total_cards": data.get("total", 0),
            "logo_url": data.get("images", {}).get("logo", ""),
            "symbol_url": data.get("images", {}).get("symbol", ""),
        }


async def _fetch_pokemon_top_cards(set_code: str, limit: int = 5) -> list[dict]:
    """Fetch all cards for a Pokemon set, sort by cardmarket EUR price, return top N."""
    settings = get_settings()
    headers = {}
    if settings.pokemon_tcg_api_key:
        headers["X-Api-Key"] = settings.pokemon_tcg_api_key

    all_cards = []
    page = 1
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                "https://api.pokemontcg.io/v2/cards",
                params={"q": f"set.id:{set_code}", "pageSize": 250, "page": page},
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            body = resp.json()
            cards = body.get("data", [])
            all_cards.extend(cards)
            if len(cards) < 250:
                break
            page += 1

    def get_best_price(card):
        """Try cardmarket EUR first, then tcgplayer USD market as fallback."""
        try:
            val = card["cardmarket"]["prices"]["averageSellPrice"]
            if val:
                return val
        except (KeyError, TypeError):
            pass
        # Fallback: tcgplayer market price (check all subtypes)
        try:
            prices = card["tcgplayer"]["prices"]
            for subtype in ("holofoil", "reverseHolofoil", "normal", "1stEditionHolofoil"):
                if subtype in prices and prices[subtype].get("market"):
                    return prices[subtype]["market"]
        except (KeyError, TypeError):
            pass
        return 0

    all_cards.sort(key=get_best_price, reverse=True)
    top = all_cards[:limit]
    return [
        {
            "name": c.get("name", ""),
            "image_url": c.get("images", {}).get("small", ""),
            "price_eur": get_best_price(c) or None,
        }
        for c in top
    ]


# ---------------------------------------------------------------------------
# Scryfall API
# ---------------------------------------------------------------------------

async def _fetch_scryfall_set(set_code: str) -> dict:
    """Fetch set metadata from Scryfall."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.scryfall.com/sets/{set_code}",
            headers={"User-Agent": "TCGPriceTracker/1.0"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "set_name": data["name"],
            "release_date": data.get("released_at"),
            "total_cards": data.get("card_count", 0),
            "logo_url": data.get("icon_svg_uri", ""),
            "symbol_url": data.get("icon_svg_uri", ""),
        }


async def _fetch_scryfall_top_cards(set_code: str, limit: int = 5) -> list[dict]:
    """Fetch top cards by EUR price from Scryfall (server-side sorted)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.scryfall.com/cards/search",
            params={"q": f"e:{set_code}", "order": "eur", "dir": "desc"},
            headers={"User-Agent": "TCGPriceTracker/1.0"},
            timeout=30,
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        cards = resp.json().get("data", [])[:limit]
        result = []
        for c in cards:
            image_url = ""
            if "image_uris" in c:
                image_url = c["image_uris"].get("small", "")
            elif "card_faces" in c and c["card_faces"]:
                image_url = c["card_faces"][0].get("image_uris", {}).get("small", "")
            eur = c.get("prices", {}).get("eur")
            result.append({
                "name": c.get("name", ""),
                "image_url": image_url,
                "price_eur": float(eur) if eur else None,
            })
        return result


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

async def get_or_refresh_set_cache(
    db: AsyncSession, set_code: str, tcg: str
) -> SetCache:
    """Return cached set data, fetching from API if stale or missing."""
    normalized = set_code.lower()

    result = await db.execute(
        select(SetCache).where(SetCache.set_code == normalized)
    )
    cached = result.scalar_one_or_none()

    if cached and (datetime.utcnow() - cached.fetched_at) < timedelta(hours=CACHE_TTL_HOURS):
        return cached

    try:
        if tcg == TCG.POKEMON or tcg == "pokemon":
            set_info = await _fetch_pokemon_set(normalized)
            top_cards = await _fetch_pokemon_top_cards(normalized)
        else:
            set_info = await _fetch_scryfall_set(normalized)
            top_cards = await _fetch_scryfall_top_cards(normalized)
    except Exception as e:
        logger.error("Failed to fetch set data for %s: %s", normalized, e)
        if cached:
            return cached
        # Create a minimal cache entry from DB data
        set_info = {"set_name": "", "release_date": None, "total_cards": 0, "logo_url": "", "symbol_url": ""}
        top_cards = []

    if cached:
        for k, v in set_info.items():
            setattr(cached, k, v)
        cached.top_cards_json = json.dumps(top_cards)
        cached.fetched_at = datetime.utcnow()
    else:
        cached = SetCache(
            set_code=normalized,
            tcg=tcg,
            **set_info,
            top_cards_json=json.dumps(top_cards),
        )
        db.add(cached)

    await db.commit()
    await db.refresh(cached)
    return cached


# ---------------------------------------------------------------------------
# Set list
# ---------------------------------------------------------------------------

async def get_set_list(db: AsyncSession, tcg_filter: str | None = None) -> list[dict]:
    """Get all distinct sets from products with product counts."""
    query = (
        select(
            Product.set_code,
            Product.set_name,
            Product.tcg,
            func.min(Product.release_date).label("release_date"),
            func.count(Product.id).label("product_count"),
        )
        .where(Product.set_code != "")
        .group_by(Product.set_code, Product.set_name, Product.tcg)
    )
    if tcg_filter:
        query = query.where(Product.tcg == tcg_filter)
    query = query.order_by(func.min(Product.release_date).desc())

    result = await db.execute(query)
    rows = result.all()

    sets = []
    for row in rows:
        # Try to get cached logo
        cache_result = await db.execute(
            select(SetCache.logo_url).where(SetCache.set_code == row.set_code.lower())
        )
        logo = cache_result.scalar_one_or_none() or ""
        sets.append({
            "set_code": row.set_code,
            "tcg": row.tcg,
            "set_name": row.set_name,
            "release_date": row.release_date,
            "logo_url": logo,
            "product_count": row.product_count,
        })
    return sets


# ---------------------------------------------------------------------------
# Booster value calculation
# ---------------------------------------------------------------------------

async def get_booster_values(
    db: AsyncSession, products: list[Product], top_card_value: float | None
) -> list[dict]:
    """Calculate price-per-booster and value score for each product."""
    values = []
    for p in products:
        lowest = await get_lowest_prices(db, p.id)
        # Find the absolute lowest price across all marketplaces
        prices_available = [v for v in lowest.values() if v is not None]
        best_price = min(prices_available) if prices_available else None

        packs = effective_pack_count(p)
        price_per_pack = best_price / packs if best_price else None

        value_score = None
        if top_card_value and best_price and best_price > 0:
            value_score = round(top_card_value / best_price, 2)

        values.append({
            "product": p,
            "lowest_price": best_price,
            "pack_count": packs,
            "price_per_pack": round(price_per_pack, 2) if price_per_pack else None,
            "top_card_value": top_card_value,
            "value_score": value_score,
        })

    # Sort by price_per_pack ascending (cheapest first), None values last
    values.sort(key=lambda x: x["price_per_pack"] if x["price_per_pack"] is not None else float("inf"))
    return values


# ---------------------------------------------------------------------------
# Top deals (global ranking)
# ---------------------------------------------------------------------------

async def get_top_deals(db: AsyncSession, limit: int = 10) -> list[dict]:
    """Get the top N cheapest booster deals across all sets."""
    # Get all products that have packs > 1 (displays, bundles, ETBs)
    result = await db.execute(
        select(Product)
        .where(Product.set_code != "")
        .options(selectinload(Product.marketplace_links))
    )
    products = result.scalars().all()

    deals = []
    for p in products:
        packs = effective_pack_count(p)
        if packs <= 1:
            continue  # Skip single boosters/blisters

        lowest = await get_lowest_prices(db, p.id)
        prices_available = [v for v in lowest.values() if v is not None]
        best_price = min(prices_available) if prices_available else None

        if best_price is None:
            continue

        price_per_pack = best_price / packs

        deals.append({
            "product": p,
            "lowest_price": best_price,
            "pack_count": packs,
            "price_per_pack": round(price_per_pack, 2),
            "top_card_value": None,
            "value_score": None,
        })

    deals.sort(key=lambda x: x["price_per_pack"])
    return deals[:limit]


# ---------------------------------------------------------------------------
# Prefetch logos for all sets (called on startup)
# ---------------------------------------------------------------------------

async def prefetch_set_logos(db: AsyncSession) -> int:
    """Fetch and cache set metadata (logo, card count, etc.) for all sets in the DB.

    Only fetches set info (not top cards) to stay within rate limits.
    Skips sets that already have a cached logo.
    """
    import asyncio

    # Get all distinct set_code + tcg pairs
    result = await db.execute(
        select(Product.set_code, Product.tcg)
        .where(Product.set_code != "")
        .group_by(Product.set_code, Product.tcg)
    )
    rows = result.all()

    fetched = 0
    for row in rows:
        code = row.set_code.lower()
        tcg = row.tcg

        # Skip if already cached
        existing = await db.execute(
            select(SetCache).where(SetCache.set_code == code)
        )
        if existing.scalar_one_or_none():
            continue

        try:
            if tcg == TCG.POKEMON or tcg == "pokemon":
                set_info = await _fetch_pokemon_set(code)
                # Pokemon TCG API: stay under 30 req/min for unauthenticated
                await asyncio.sleep(0.5)
            else:
                set_info = await _fetch_scryfall_set(code)
                # Scryfall wants 50-75ms between requests
                await asyncio.sleep(0.15)

            cache = SetCache(
                set_code=code,
                tcg=tcg,
                **set_info,
                top_cards_json="[]",
            )
            db.add(cache)
            await db.commit()
            fetched += 1
            logger.info("Prefetched logo for set %s (%s)", code, set_info.get("set_name", ""))
        except Exception as e:
            logger.warning("Failed to prefetch set %s: %s: %s", code, type(e).__name__, e)
            await db.rollback()
            await asyncio.sleep(1)

    return fetched
