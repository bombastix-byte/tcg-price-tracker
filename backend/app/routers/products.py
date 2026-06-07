from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Product, MarketplaceLink, TCG, Category
from app.schemas import (
    ProductCreate,
    ProductOut,
    ProductWithPrices,
    MarketplaceLinkCreate,
    MarketplaceLinkOut,
)
from app.services.price_service import get_lowest_prices

router = APIRouter()


@router.get("/", response_model=list[ProductOut])
async def list_products(
    tcg: TCG | None = None,
    category: Category | None = None,
    search: str | None = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """List products with optional filters."""
    query = select(Product)
    if tcg:
        query = query.where(Product.tcg == tcg)
    if category:
        query = query.where(Product.category == category)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    query = query.order_by(Product.name)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductWithPrices)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a product with its lowest prices and marketplace links."""
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.marketplace_links))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    lowest = await get_lowest_prices(db, product_id)
    return ProductWithPrices(
        **{c.name: getattr(product, c.name) for c in Product.__table__.columns},
        lowest_prices=lowest,
        marketplace_links=[
            MarketplaceLinkOut.model_validate(link)
            for link in product.marketplace_links
        ],
    )


@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Add a new product."""
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.post("/{product_id}/links", response_model=MarketplaceLinkOut, status_code=201)
async def create_marketplace_link(
    product_id: int,
    data: MarketplaceLinkCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a marketplace link to a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for duplicate marketplace link
    existing = await db.execute(
        select(MarketplaceLink).where(
            MarketplaceLink.product_id == product_id,
            MarketplaceLink.marketplace == data.marketplace,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Link for {data.marketplace.value} already exists",
        )

    link = MarketplaceLink(product_id=product_id, **data.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


@router.delete("/{product_id}/links/{link_id}", status_code=204)
async def delete_marketplace_link(
    product_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a marketplace link."""
    result = await db.execute(
        select(MarketplaceLink).where(
            MarketplaceLink.id == link_id,
            MarketplaceLink.product_id == product_id,
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await db.delete(link)
    await db.commit()
