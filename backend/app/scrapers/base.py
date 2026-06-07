from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScrapedPrice:
    marketplace: str
    price: float
    currency: str
    condition: str
    seller: str
    url: str
    scraped_at: datetime


class BaseScraper(ABC):
    """Abstract base class for marketplace scrapers."""

    @abstractmethod
    async def search(self, query: str, tcg: str = "") -> list[ScrapedPrice]:
        """Search marketplace for a product and return prices."""

    @abstractmethod
    async def get_price(self, product_name: str, **kwargs) -> list[ScrapedPrice]:
        """Get current prices for a specific product."""

    async def get_price_by_url(self, url: str) -> list[ScrapedPrice]:
        """Get price directly from a product URL. Override in subclasses."""
        return []

    async def close(self):
        """Clean up resources."""
