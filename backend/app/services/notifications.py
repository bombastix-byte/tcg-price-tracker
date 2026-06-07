import logging

import aiohttp

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_push_notification(
    device_token: str, title: str, body: str, data: dict | None = None
) -> bool:
    """Send a push notification via Expo Push API."""
    settings = get_settings()
    message = {
        "to": device_token,
        "sound": "default",
        "title": title,
        "body": body,
    }
    if data:
        message["data"] = data

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.expo_push_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("data", {}).get("status") == "ok":
                        return True
                    logger.warning("Push notification error: %s", result)
                else:
                    logger.warning("Push API returned %d", resp.status)
    except aiohttp.ClientError as e:
        logger.error("Push notification failed: %s", e)

    return False


async def notify_price_alert(
    device_token: str,
    product_name: str,
    current_price: float,
    target_price: float,
    marketplace: str,
) -> bool:
    """Send a price alert notification."""
    title = "Price Alert!"
    body = (
        f"{product_name} is now {current_price:.2f}EUR on {marketplace} "
        f"(target: {target_price:.2f}EUR)"
    )
    return await send_push_notification(
        device_token, title, body, data={"type": "price_alert"}
    )
