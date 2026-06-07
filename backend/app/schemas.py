from datetime import datetime
from pydantic import BaseModel
from app.models import TCG, Category, Marketplace, AlertDirection


# --- Product ---

class ProductCreate(BaseModel):
    name: str
    tcg: TCG
    category: Category
    set_name: str = ""
    set_code: str = ""
    image_url: str = ""
    release_date: str | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    tcg: TCG
    category: Category
    set_name: str
    set_code: str
    image_url: str
    release_date: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- MarketplaceLink ---

class MarketplaceLinkCreate(BaseModel):
    marketplace: Marketplace
    url: str = ""
    external_id: str = ""


class MarketplaceLinkOut(BaseModel):
    id: int
    product_id: int
    marketplace: Marketplace
    url: str
    external_id: str

    model_config = {"from_attributes": True}


class ProductWithPrices(ProductOut):
    lowest_prices: dict[str, float | None] = {}
    marketplace_links: list[MarketplaceLinkOut] = []


# --- Price ---

class PriceOut(BaseModel):
    id: int
    product_id: int
    marketplace: Marketplace
    price: float
    currency: str
    condition: str
    seller: str
    url: str
    scraped_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryPoint(BaseModel):
    date: str
    cardmarket: float | None = None
    ebay: float | None = None
    amazon: float | None = None


# --- Alert ---

class AlertCreate(BaseModel):
    product_id: int
    user_device_token: str
    target_price: float
    direction: AlertDirection


class AlertOut(BaseModel):
    id: int
    product_id: int
    user_device_token: str
    target_price: float
    direction: AlertDirection
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    target_price: float | None = None
    direction: AlertDirection | None = None
    is_active: bool | None = None
