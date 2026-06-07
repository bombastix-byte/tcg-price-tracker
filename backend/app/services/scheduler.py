import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session
from app.models import Product, Alert, Price, AlertDirection
from app.services.price_service import update_prices_for_product
from app.services.notifications import notify_price_alert

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def update_all_prices():
    """Fetch fresh prices for all products and check alerts."""
    logger.info("Starting scheduled price update...")
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

        for product in products:
            try:
                new_prices = await update_prices_for_product(session, product.id)
                if new_prices:
                    await check_alerts_for_product(session, product, new_prices)
            except Exception as e:
                logger.error("Failed to update prices for %s: %s", product.name, e)

    logger.info("Scheduled price update complete.")


async def check_alerts_for_product(session, product: Product, new_prices: list[Price]):
    """Check if any alerts should fire for the given product prices."""
    result = await session.execute(
        select(Alert).where(Alert.product_id == product.id, Alert.is_active == True)
    )
    alerts = result.scalars().all()

    for alert in alerts:
        for price in new_prices:
            should_notify = False
            if alert.direction == AlertDirection.BELOW and price.price <= alert.target_price:
                should_notify = True
            elif alert.direction == AlertDirection.ABOVE and price.price >= alert.target_price:
                should_notify = True

            if should_notify:
                success = await notify_price_alert(
                    device_token=alert.user_device_token,
                    product_name=product.name,
                    current_price=price.price,
                    target_price=alert.target_price,
                    marketplace=price.marketplace,
                )
                if success:
                    alert.is_active = False
                    await session.commit()
                break


def start_scheduler():
    settings = get_settings()
    scheduler.add_job(
        update_all_prices,
        "interval",
        hours=settings.price_update_interval_hours,
        id="price_update",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started (interval: %dh)", settings.price_update_interval_hours)


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")
