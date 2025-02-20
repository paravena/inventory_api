import pytest
import json
from app.models.product import Product

def test_get_products_empty(client, database):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 0
    assert len(data['items']) == 0

def test_get_products_with_data(client, database, sample_product):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 1
    assert len(data['items']) == 1
    assert data['items'][0]['id'] == sample_product.id
    assert data['items'][0]['name'] == 'Test Product'

def test_get_products_with_filters(client, database):
    # Create products with different categories and prices
    products = [
        Product(id='1', name='Product 1', category='Electronics', price=100, sku='SKU-001'),
        Product(id='2', name='Product 2', category='Electronics', price=200, sku='SKU-002'),
        Product(id='3', name='Product 3', category='Books', price=50, sku='SKU-003')
    ]
    for product in products:
        database.session.add(product)
    database.session.commit()

    # Test category filter
    response = client.get('/api/products?category=Electronics')
    data = json.loads(response.data)
    assert data['total'] == 2
    assert all(item['category'] == 'Electronics' for item in data['items'])

    # Test price range filter
    response = client.get('/api/products?min_price=100&max_price=150')
    data = json.loads(response.data)
    assert data['total'] == 1
    assert data['items'][0]['price'] == 100.0

def test_get_product_by_id(client, database, sample_product):
    response = client.get(f'/api/products/{sample_product.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == sample_product.id
    assert data['name'] == 'Test Product'

def test_get_product_not_found(client, database):
    response = client.get('/api/products/nonexistent-id')
    assert response.status_code == 404

def test_create_product_success(client, database):
    product_data = {
        'name': 'New Product',
        'category': 'New Category',
        'price': 15.99,
        'sku': 'NEW-SKU-001',
        'description': 'New Description'
    }
    response = client.post('/api/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == product_data['name']
    assert data['sku'] == product_data['sku']

def test_create_product_missing_fields(client, database):
    product_data = {
        'name': 'New Product',
        'category': 'New Category'
        # Missing required fields
    }
    response = client.post('/api/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_product_duplicate_sku(client, database, sample_product):
    product_data = {
        'name': 'Another Product',
        'category': 'Another Category',
        'price': 20.99,
        'sku': 'TEST-SKU-001'  # Same SKU as sample_product
    }
    response = client.post('/api/products', 
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'SKU already exists'

def test_update_product_success(client, database, sample_product):
    update_data = {
        'name': 'Updated Product',
        'price': 25.99
    }
    response = client.put(f'/api/products/{sample_product.id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == update_data['name']
    assert data['price'] == update_data['price']

def test_update_product_not_found(client, database):
    update_data = {'name': 'Updated Product'}
    response = client.put('/api/products/nonexistent-id',
                         data=json.dumps(update_data),
                         content_type='application/json')
    assert response.status_code == 404

def test_delete_product_success(client, database, sample_product):
    response = client.delete(f'/api/products/{sample_product.id}')
    assert response.status_code == 204
    assert Product.query.get(sample_product.id) is None

def test_delete_product_with_inventory(client, database, sample_inventory):
    response = client.delete(f'/api/products/{sample_inventory.product_id}')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Cannot delete product with existing inventory'
