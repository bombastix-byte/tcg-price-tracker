from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import products, prices, alerts
from app.services.scheduler import start_scheduler, stop_scheduler
from app.seed import seed_sample_products


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_sample_products()
    start_scheduler()
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


@app.get("/")
async def root():
    return {"message": "TCG Price Tracker API", "docs": "/docs"}
