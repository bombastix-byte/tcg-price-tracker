from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import logging

from app.database import init_db, async_session
from app.routers import products, prices, alerts, sets
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.set_service import prefetch_set_logos
from app.seed import seed_sample_products

logger = logging.getLogger(__name__)


async def _prefetch_logos_background():
    """Prefetch set logos in the background after startup."""
    await asyncio.sleep(1)  # Let the server start first
    try:
        async with async_session() as db:
            count = await prefetch_set_logos(db)
            if count:
                logger.info("Prefetched logos for %d sets", count)
    except Exception as e:
        logger.warning("Logo prefetch failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_sample_products()
    start_scheduler()
    # Fire-and-forget background task for logo prefetching
    asyncio.create_task(_prefetch_logos_background())
    yield
    stop_scheduler()


app = FastAPI(title="TCG Price Tracker", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(prices.router, prefix="/prices", tags=["prices"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(sets.router, prefix="/sets", tags=["sets"])


@app.get("/")
async def root():
    return {"message": "TCG Price Tracker API", "docs": "/docs"}
