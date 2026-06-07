from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "TCG Price Tracker"
    database_url: str = "sqlite+aiosqlite:///./tcg_prices.db"

    # Cardmarket API (OAuth 1.0)
    cardmarket_app_token: str = ""
    cardmarket_app_secret: str = ""
    cardmarket_access_token: str = ""
    cardmarket_access_secret: str = ""

    # eBay Browse API (OAuth 2.0)
    ebay_client_id: str = ""
    ebay_client_secret: str = ""

    # Scheduler
    price_update_interval_hours: int = 6

    # Expo Push Notifications
    expo_push_url: str = "https://exp.host/--/api/v2/push/send"

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
