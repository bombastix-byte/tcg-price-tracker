from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Alert, Product
from app.schemas import AlertCreate, AlertOut, AlertUpdate

router = APIRouter()


@router.get("/", response_model=list[AlertOut])
async def list_alerts(
    device_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List alerts for a device."""
    result = await db.execute(
        select(Alert)
        .where(Alert.user_device_token == device_token)
        .order_by(Alert.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(data: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a new price alert."""
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: int, data: AlertUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an alert (e.g. deactivate or change target price)."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)

    await db.commit()
    await db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()
