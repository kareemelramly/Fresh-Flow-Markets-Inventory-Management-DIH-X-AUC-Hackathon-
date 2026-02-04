# Fresh Flow Markets API

REST API for inventory management system built for the Deloitte x AUC Hackathon.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Inventory Management

#### Get All Items
```http
GET /api/inventory/items?page=1&per_page=50&search=pizza
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "Margherita Pizza",
      "barcode": "1234567890",
      "price": 12.99,
      "current_stock": 45,
      "minimum_stock": 20
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 87276,
    "pages": 1746
  }
}
```

#### Get Item Details
```http
GET /api/inventory/items/123
```

#### Update Item
```http
PUT /api/inventory/items/123
Content-Type: application/json

{
  "current_stock": 50,
  "minimum_stock": 25,
  "price": 13.99
}
```

#### Get Low Stock Items
```http
GET /api/inventory/low-stock
```

### Orders

#### Get Orders
```http
GET /api/orders?status=Closed&place_id=59821&page=1&per_page=50
```

Query Parameters:
- `status` - Filter by order status
- `place_id` - Filter by place/restaurant
- `start_date` - Filter by start date (ISO format)
- `end_date` - Filter by end date
- `page` - Page number
- `per_page` - Items per page

#### Get Order Details
```http
GET /api/orders/60825
```

Response includes order details and all order items.

### Analytics

#### Dashboard Statistics
```http
GET /api/analytics/dashboard?days=30
```

Returns:
- Total orders, revenue, average order value
- Order counts by status
- Top 10 selling items
- Daily revenue trend

#### Place Analytics
```http
GET /api/analytics/places?days=30
```

Returns revenue and order statistics for each restaurant/place.

### Demand Forecasting

#### Forecast Item Demand
```http
POST /api/forecast/demand
Content-Type: application/json

{
  "item_id": 123,
  "days": 7
}
```

Returns:
- Historical average daily demand
- 7-day forecast
- Reorder recommendation

### Places/Restaurants

#### Get All Places
```http
GET /api/places
```

#### Get Place Details
```http
GET /api/places/59821
```

## Database Schema

The API uses SQLite database `fresh_flow_markets.db` with 18 tables:

**Dimension Tables:**
- `dim_items` - Inventory items (87,276 rows)
- `dim_users` - Users (22,955 rows)
- `dim_places` - Restaurants/locations (1,824 rows)
- `dim_campaigns` - Marketing campaigns
- `dim_add_ons` - Item add-ons
- And more...

**Fact Tables:**
- `fct_orders` - Order transactions (399,810 rows)
- `fct_order_items` - Order line items (1,999,341 rows)
- `fct_cash_balances` - Cash transactions
- And more...

See [DATABASE_SCHEMA.md](database/DATABASE_SCHEMA.md) for complete documentation.

## Error Handling

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## CORS

CORS is enabled for all origins to support frontend integration.

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Connection
The API uses SQLite for simplicity. For production, update `src/api/__init__.py` to use PostgreSQL or MySQL.

## Production Deployment

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_PATH=/path/to/database.db
```

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

Built for Deloitte x AUC Hackathon - Fresh Flow Markets Team
