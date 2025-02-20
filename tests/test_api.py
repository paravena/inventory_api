import pytest
from app.main import create_app, db
from app.models.product import Product
from app.models.inventory import Inventory
import uuid
import json

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_product(database):
    product = Product(
        id=str(uuid.uuid4()),
        name='Test Product',
        description='Test Description',
        category='Test Category',
        price=10.99,
        sku='TEST-SKU-001'
    )
    database.session.add(product)
    database.session.commit()
    return product

def test_create_inventory_success(client, database, sample_product):
    store_id = 'STORE-001'
    response = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': sample_product.id,
            'quantity': 100,
            'min_stock': 10
        }
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['store_id'] == store_id
    assert data['product_id'] == sample_product.id
    assert data['quantity'] == 100
    assert data['min_stock'] == 10
    assert 'product' in data
    assert data['product']['id'] == sample_product.id

def test_create_inventory_invalid_quantity(client, database, sample_product):
    store_id = 'STORE-001'
    response = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': sample_product.id,
            'quantity': 0,
            'min_stock': 10
        }
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Quantity must be greater than 0' in data['message']

def test_create_inventory_invalid_min_stock(client, database, sample_product):
    store_id = 'STORE-001'
    response = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': sample_product.id,
            'quantity': 100,
            'min_stock': 0
        }
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Minimum stock must be greater than 0' in data['message']

def test_create_inventory_nonexistent_product(client, database):
    store_id = 'STORE-001'
    response = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': str(uuid.uuid4()),
            'quantity': 100,
            'min_stock': 10
        }
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'Product not found' in data['message']

def test_create_duplicate_inventory(client, database, sample_product):
    store_id = 'STORE-001'
    # Create first inventory
    response1 = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': sample_product.id,
            'quantity': 100,
            'min_stock': 10
        }
    )
    assert response1.status_code == 201

    # Try to create duplicate inventory
    response2 = client.post(
        f'/api/inventory/stores/{store_id}/inventory',
        json={
            'product_id': sample_product.id,
            'quantity': 200,
            'min_stock': 20
        }
    )
    
    assert response2.status_code == 400
    data = json.loads(response2.data)
    assert 'Inventory already exists for this product in the store' in data['message']
