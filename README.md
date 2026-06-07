# TCG Price Tracker

Price comparison app for sealed TCG products (Pokemon, Magic: The Gathering) across Cardmarket, eBay, and Amazon.

## Project Structure

```
tcg-price-tracker/
├── backend/          Python FastAPI backend
│   ├── app/
│   │   ├── main.py           FastAPI entry point
│   │   ├── models.py         SQLAlchemy models
│   │   ├── schemas.py        Pydantic schemas
│   │   ├── routers/          API endpoints
│   │   ├── scrapers/         Marketplace scrapers
│   │   └── services/         Business logic & scheduler
│   ├── requirements.txt
│   └── Dockerfile
└── mobile/           React Native (Expo) app
    ├── app/              Screens (file-based routing)
    ├── components/       Reusable UI components
    └── services/         API client
```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env         # Edit with your API keys

uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs

## Mobile Setup

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with Expo Go on your phone.

**Note:** Update `API_BASE` in `mobile/services/api.ts` with your backend URL:
- Android emulator: `http://10.0.2.2:8000`
- iOS simulator: `http://localhost:8000`
- Physical device: `http://<your-local-ip>:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products (filter by tcg, category, search) |
| GET | `/products/{id}` | Product detail with lowest prices |
| POST | `/products/` | Add a product |
| GET | `/prices/products/{id}/prices` | Current prices |
| POST | `/prices/products/{id}/prices/refresh` | Trigger fresh price fetch |
| GET | `/prices/products/{id}/history` | Price history |
| GET | `/alerts/?device_token=...` | List alerts |
| POST | `/alerts/` | Create alert |
| PATCH | `/alerts/{id}` | Update alert |
| DELETE | `/alerts/{id}` | Delete alert |

## Marketplace Configuration

- **Cardmarket**: Works via web scraping by default. For API access, add OAuth 1.0 credentials to `.env`.
- **eBay**: Requires Browse API credentials (OAuth 2.0 Client Credentials). Register at https://developer.ebay.com.
- **Amazon**: Uses web scraping with rotating user-agents. Rate-limited. For production, use the Product Advertising API.
