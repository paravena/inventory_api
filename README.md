# Inventory Management API

A robust RESTful API for managing product inventory across multiple stores, built with Flask and PostgreSQL.

## Description

This API provides a comprehensive solution for inventory management, featuring:
- Product management (CRUD operations)
- Store-specific inventory tracking
- Inter-store inventory transfers
- Low stock alerts
- Detailed movement history

## Key Features

- RESTful API design with Swagger documentation
- Pagination and filtering capabilities
- Real-time inventory tracking
- Automated low stock alerts
- Secure transfer operations with validation
- Detailed audit trail of all inventory movements

## Prerequisites

- Docker and Docker Compose installed on your system
- Python 3.8 or higher
- pip (Python package manager)

## Setup Instructions

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   POSTGRES_DB=inventory
   POSTGRES_USER=inventory_user
   POSTGRES_PASSWORD=your_password
   DATABASE_URL=postgresql://inventory_user:your_password@localhost:5432/inventory
   FLASK_APP=app.main:app
   FLASK_ENV=development
   FLASK_RUN_PORT=3000
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the PostgreSQL database:
   ```bash
   docker-compose up -d
   ```

5. Run the application:
   ```bash
   # Make sure your virtual environment is activated
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows

   # Run the application using Flask CLI
   # The application will use environment variables from .env file
   flask run
   ```

The API will be available at `http://localhost:3000`
Swagger documentation can be accessed at `http://localhost:3000/api/docs`

## API Documentation

### Products API

#### GET /api/products
- List all products with optional filters
- Supports pagination (page, per_page parameters)
- Filter by category, price range, and minimum stock level
- Returns paginated list of products with total count

#### POST /api/products
- Create a new product
- Required fields: name, category, price, SKU
- Validates SKU uniqueness
- Returns created product details

#### GET /api/products/{id}
- Get product details by ID
- Returns 404 if product not found

#### PUT /api/products/{id}
- Update product information
- Validates SKU uniqueness if changed
- Returns updated product details

#### DELETE /api/products/{id}
- Delete a product
- Prevents deletion if inventory exists
- Returns 204 on success

### Inventory API

#### GET /api/stores/{store_id}/inventory
- Get inventory for a specific store
- Returns list of inventory items with product details

#### POST /api/inventory/transfer
- Transfer inventory between stores
- Required fields: product_id, source_store_id, target_store_id, quantity
- Validates source inventory availability
- Creates movement history
- Returns transfer details

#### GET /api/inventory/alerts
- Get alerts for items below minimum stock level
- Returns list of inventory items with alert details

## Design Decisions

1. **Database Schema**
   - UUID primary keys for distributed system compatibility
   - Relationships between products, inventory, and movements
   - Minimum stock levels for automated alerts

2. **API Design**
   - RESTful architecture with proper HTTP methods
   - Comprehensive input validation
   - Proper error handling with meaningful status codes
   - Swagger documentation for API exploration

3. **Security & Data Integrity**
   - Input validation on all endpoints
   - Transaction integrity for transfers
   - Protection against negative inventory
   - SKU uniqueness enforcement

4. **Scalability**
   - Pagination for large datasets
   - Efficient database queries with proper indexing
   - Docker containerization for deployment
   - Store-based partitioning for data organization

5. **Monitoring & Tracking**
   - Low stock alerts system
   - Movement history for audit trails
   - Endpoint logging for monitoring

## Database Management

### Database Schema

The application uses three main tables:

1. **Products Table**
   - `id` (UUID): Primary key
   - `name` (String): Product name
   - `description` (Text): Product description
   - `category` (String): Product category
   - `price` (Numeric): Product price
   - `sku` (String): Unique product identifier
   - `created_at` (DateTime): Creation timestamp
   - `updated_at` (DateTime): Last update timestamp

2. **Inventory Table**
   - `id` (UUID): Primary key
   - `product_id` (UUID): Foreign key to Products
   - `store_id` (UUID): Store identifier
   - `quantity` (Integer): Current stock quantity
   - `min_stock` (Integer): Minimum stock level
   - `created_at` (DateTime): Creation timestamp
   - `updated_at` (DateTime): Last update timestamp

3. **Movements Table**
   - `id` (UUID): Primary key
   - `product_id` (UUID): Foreign key to Products
   - `source_store_id` (UUID): Source store for transfer
   - `target_store_id` (UUID): Target store for transfer
   - `quantity` (Integer): Movement quantity
   - `timestamp` (DateTime): Movement timestamp
   - `type` (Enum): Movement type (IN/OUT/TRANSFER)

### Database Setup

1. Start the PostgreSQL container:
   ```bash
   docker-compose up -d
   ```

2. Initialize the database tables:
   ```bash
   # Option 1: Using Flask CLI
   flask run

   # Option 2: Using Python directly
   python wsgi.py
   ```
   The tables will be automatically created when the application starts.

3. View database logs:
   ```bash
   docker-compose logs postgres
   ```

- Stop the database:
  ```bash
  docker-compose down
  ```

- Data persistence through Docker volume: `postgres_data`

## Testing

Run the test suite:
```bash
pip install -r requirements-test.txt
pytest
```

Coverage reports are available in the htmlcov directory after running tests.
