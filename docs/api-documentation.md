# API Documentation

## Overview

The Inventory Management API provides endpoints for managing products, stores, and inventory. All endpoints follow RESTful principles and return JSON responses.

## Base URL

```
http://localhost:3000
```

Swagger documentation is available at:
```
http://localhost:3000/api/docs
```

## Authentication

Currently, the API does not require authentication. This might change in future versions.

## Common Response Formats

### Success Response
```json
{
    "data": {
        // Response data
    },
    "message": "Operation successful"
}
```

### Error Response
```json
{
    "error": "Error message",
    "status_code": 400
}
```

## Endpoints

### Products API

#### GET /api/products
List all products with optional filters.

**Query Parameters:**
- `page` (integer, optional): Page number for pagination
- `per_page` (integer, optional): Items per page
- `category` (string, optional): Filter by category
- `min_price` (float, optional): Minimum price filter
- `max_price` (float, optional): Maximum price filter
- `min_stock` (integer, optional): Minimum stock level filter

**Response:**
```json
{
    "items": [
        {
            "id": "string",
            "name": "string",
            "description": "string",
            "category": "string",
            "price": 0.0,
            "sku": "string"
        }
    ],
    "total": 0,
    "page": 1,
    "per_page": 10,
    "pages": 1
}
```

#### POST /api/products
Create a new product.

**Request Body:**
```json
{
    "name": "string",
    "description": "string",
    "category": "string",
    "price": 0.0,
    "sku": "string"
}
```

**Response:** Created product object

#### GET /api/products/{id}
Get product details by ID.

**Parameters:**
- `id` (string): Product ID

**Response:** Product object

#### PUT /api/products/{id}
Update product information.

**Parameters:**
- `id` (string): Product ID

**Request Body:** Same as POST /api/products

**Response:** Updated product object

#### DELETE /api/products/{id}
Delete a product.

**Parameters:**
- `id` (string): Product ID

**Response:** 204 No Content

### Inventory API

#### GET /api/stores/{store_id}/inventory
Get inventory for a specific store.

**Parameters:**
- `store_id` (string): Store ID
- `low_stock` (boolean, optional): Filter for low stock items only

**Response:**
```json
{
    "items": [
        {
            "id": "string",
            "product_id": "string",
            "store_id": "string",
            "quantity": 0,
            "min_stock_level": 0
        }
    ],
    "total": 0
}
```

#### POST /api/stores/{store_id}/inventory
Create inventory entry for a product in a store.

**Parameters:**
- `store_id` (string): Store ID

**Request Body:**
```json
{
    "product_id": "string",
    "quantity": 0,
    "min_stock_level": 0
}
```

**Response:** Created inventory object

#### POST /api/inventory/transfer
Transfer inventory between stores.

**Request Body:**
```json
{
    "product_id": "string",
    "from_store_id": "string",
    "to_store_id": "string",
    "quantity": 0
}
```

**Response:**
```json
{
    "message": "Transfer successful",
    "from_store": {
        "store_id": "string",
        "new_quantity": 0
    },
    "to_store": {
        "store_id": "string",
        "new_quantity": 0
    }
}
```

#### GET /api/inventory/alerts
Get low stock alerts across all stores.

**Query Parameters:**
- `store_id` (string, optional): Filter by store

**Response:**
```json
{
    "alerts": [
        {
            "store_id": "string",
            "product_id": "string",
            "current_quantity": 0,
            "min_stock_level": 0
        }
    ]
}
```

## Error Codes

- 400: Bad Request - Invalid input data
- 404: Not Found - Resource not found
- 409: Conflict - Resource already exists
- 422: Unprocessable Entity - Business rule violation
- 500: Internal Server Error - Server-side error

## Rate Limiting

The API currently does not implement rate limiting, but it's recommended to keep request rates reasonable.

## Versioning

The current API version is v1. The version is included in the URL path: `/api/v1/...`

## Best Practices

1. Always include error handling in your client code
2. Use pagination for large result sets
3. Include appropriate content-type headers
4. Handle HTTP response codes appropriately
