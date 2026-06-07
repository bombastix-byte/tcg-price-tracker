from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class TCG(str, enum.Enum):
    POKEMON = "pokemon"
    MAGIC = "magic"


class Category(str, enum.Enum):
    BOOSTER_BOX = "booster_box"
    ETB = "etb"
    BLISTER = "blister"
    BOOSTER_PACK = "booster_pack"
    COLLECTION_BOX = "collection_box"
    BUNDLE = "bundle"
    OTHER = "other"


class Marketplace(str, enum.Enum):
    CARDMARKET = "cardmarket"
    EBAY = "ebay"
    AMAZON = "amazon"


class AlertDirection(str, enum.Enum):
    BELOW = "below"
    ABOVE = "above"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    tcg: Mapped[str] = mapped_column(SAEnum(TCG))
    category: Mapped[str] = mapped_column(SAEnum(Category))
    set_name: Mapped[str] = mapped_column(String(200), default="")
    set_code: Mapped[str] = mapped_column(String(20), default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    release_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    prices: Mapped[list["Price"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    marketplace_links: Mapped[list["MarketplaceLink"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    marketplace: Mapped[str] = mapped_column(SAEnum(Marketplace))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    condition: Mapped[str] = mapped_column(String(50), default="new")
    seller: Mapped[str] = mapped_column(String(200), default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="prices")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user_device_token: Mapped[str] = mapped_column(String(200))
    target_price: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(SAEnum(AlertDirection))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="alerts")


class MarketplaceLink(Base):
    __tablename__ = "marketplace_links"
    __table_args__ = (
        UniqueConstraint("product_id", "marketplace", name="uq_product_marketplace"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    marketplace: Mapped[str] = mapped_column(SAEnum(Marketplace))
    url: Mapped[str] = mapped_column(String(500), default="")
    external_id: Mapped[str] = mapped_column(String(200), default="")

    product: Mapped["Product"] = relationship(back_populates="marketplace_links")
