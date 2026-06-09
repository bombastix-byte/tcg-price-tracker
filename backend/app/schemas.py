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
    pack_count: int | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    tcg: TCG
    category: Category
    set_name: str
    set_code: str
    image_url: str
    release_date: str | None
    pack_count: int | None = None
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
    idealo: float | None = None
    geizhals: float | None = None


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


# --- Set ---

class TopCard(BaseModel):
    name: str
    image_url: str
    price_eur: float | None = None


class SetSummary(BaseModel):
    set_code: str
    tcg: TCG
    set_name: str
    release_date: str | None
    logo_url: str = ""
    product_count: int = 0


class BoosterValue(BaseModel):
    product: ProductOut
    lowest_price: float | None = None
    pack_count: int = 1
    price_per_pack: float | None = None
    top_card_value: float | None = None
    value_score: float | None = None


class SetDetail(BaseModel):
    set_code: str
    tcg: TCG
    set_name: str
    release_date: str | None
    logo_url: str = ""
    symbol_url: str = ""
    total_cards: int = 0
    top_cards: list[TopCard] = []
    sealed_products: list[ProductWithPrices] = []
    booster_values: list[BoosterValue] = []
    price_trend: list[PriceHistoryPoint] = []
