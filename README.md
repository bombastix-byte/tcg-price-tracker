# TCG Price Tracker

Price comparison app for sealed TCG products (Pokemon, Magic: The Gathering) across Cardmarket, eBay, and Amazon.

Tracks ~40 products from 2023-2025 with direct marketplace links for precise price scraping.

## Project Structure

```
tcg-price-tracker/
├── backend/          Python FastAPI backend
│   ├── app/
│   │   ├── main.py           FastAPI entry point
│   │   ├── models.py         SQLAlchemy models (Product, Price, Alert, MarketplaceLink)
│   │   ├── schemas.py        Pydantic schemas
│   │   ├── seed.py           Product seed data with marketplace URLs
│   │   ├── routers/          API endpoints
│   │   ├── scrapers/         Marketplace scrapers (Cardmarket, eBay, Amazon)
│   │   └── services/         Business logic & scheduler
│   ├── requirements.txt
│   └── Dockerfile
└── mobile/           React Native (Expo) app
    ├── app/              Screens (file-based routing)
    ├── components/       Reusable UI components
    └── services/         API client
```

## Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm
- (Optional) [Expo Go](https://expo.dev/client) app on your phone for mobile testing

## Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env         # Edit with your API keys (optional)

# Start the server
uvicorn app.main:app --reload --port 8000
```

On first start, the database is created automatically and seeded with ~38 products (Pokemon + Magic: The Gathering, 2023-2025) including Cardmarket and Amazon marketplace links.

API docs: http://localhost:8000/docs

### Seed Demo Prices

To populate price history for all products (useful for testing charts):

```bash
curl -X POST http://localhost:8000/prices/seed-demo
```

This creates 15 days of simulated price data across all three marketplaces.

## Mobile App Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo dev server
npx expo start
```

### Running the app

- **Web browser**: Press `w` in the Expo terminal, or open http://localhost:8081
- **iOS Simulator**: Press `i` (requires Xcode on macOS)
- **Android Emulator**: Press `a` (requires Android Studio)
- **Physical device**: Scan the QR code with Expo Go

### Backend URL Configuration

Update `API_BASE` in `mobile/services/api.ts` if needed:

| Platform | URL |
|----------|-----|
| Android emulator | `http://10.0.2.2:8000` |
| iOS simulator / Web | `http://localhost:8000` |
| Physical device | `http://<your-local-ip>:8000` |

## API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products (filter by `tcg`, `category`, `search`) |
| GET | `/products/{id}` | Product detail with lowest prices and marketplace links |
| POST | `/products/` | Add a product |
| POST | `/products/{id}/links` | Add a marketplace link to a product |
| DELETE | `/products/{id}/links/{link_id}` | Remove a marketplace link |

### Prices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prices/products/{id}/prices` | Current prices from all marketplaces |
| POST | `/prices/products/{id}/prices/refresh` | Trigger fresh price fetch |
| GET | `/prices/products/{id}/history?days=30` | Price history (aggregated per day) |
| POST | `/prices/seed-demo` | Seed demo price data for all products |

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts/?device_token=...` | List alerts for a device |
| POST | `/alerts/` | Create price alert |
| PATCH | `/alerts/{id}` | Update alert |
| DELETE | `/alerts/{id}` | Delete alert |

## Marketplace Configuration

All marketplace credentials are optional. Without them, the app falls back to demo data.

| Marketplace | Method | Configuration |
|------------|--------|---------------|
| **Cardmarket** | Web scraping (default) or OAuth 1.0 API | Add `CARDMARKET_*` tokens to `.env` |
| **eBay** | Browse API (OAuth 2.0 Client Credentials) | Register at https://developer.ebay.com, add `EBAY_CLIENT_ID` and `EBAY_CLIENT_SECRET` to `.env` |
| **Amazon** | Web scraping with rotating user-agents | No credentials needed (rate-limited, best-effort) |

### MarketplaceLink System

Each product can have direct URLs to its marketplace pages (stored in the `marketplace_links` table). When a link exists, the scraper fetches the product page directly instead of searching by name, resulting in more accurate pricing.

Links are pre-configured in the seed data for Cardmarket and Amazon (with ASINs). You can add or remove links via the API:

```bash
# Add an eBay link
curl -X POST http://localhost:8000/products/1/links \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "ebay", "url": "https://www.ebay.de/itm/123456", "external_id": "123456"}'

# Remove a link
curl -X DELETE http://localhost:8000/products/1/links/5
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tcg_prices.db` | Database connection string |
| `CARDMARKET_APP_TOKEN` | — | Cardmarket OAuth app token |
| `CARDMARKET_APP_SECRET` | — | Cardmarket OAuth app secret |
| `CARDMARKET_ACCESS_TOKEN` | — | Cardmarket OAuth access token |
| `CARDMARKET_ACCESS_SECRET` | — | Cardmarket OAuth access secret |
| `EBAY_CLIENT_ID` | — | eBay API client ID |
| `EBAY_CLIENT_SECRET` | — | eBay API client secret |
| `PRICE_UPDATE_INTERVAL_HOURS` | `6` | Auto-refresh interval for the scheduler |
