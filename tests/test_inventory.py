import pytest
import json
from app.models.inventory import Inventory
from app.models.movement import Movement, MovementType

def test_get_store_inventory_empty(client, database):
    response = client.get('/api/stores/STORE-001/inventory')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

def test_get_store_inventory_with_data(client, database, sample_inventory):
    response = client.get(f'/api/stores/{sample_inventory.store_id}/inventory')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['id'] == sample_inventory.id
    assert data[0]['product']['id'] == sample_inventory.product_id

def test_transfer_inventory_success(client, database, sample_inventory):
    transfer_data = {
        'product_id': sample_inventory.product_id,
        'source_store_id': sample_inventory.store_id,
        'target_store_id': 'STORE-002',
        'quantity': 50
    }
    
    response = client.post('/api/inventory/transfer',
                          data=json.dumps(transfer_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['type'] == MovementType.TRANSFER.value
    assert data['quantity'] == 50

    # Verify source inventory was decreased
    source_inventory = Inventory.query.get(sample_inventory.id)
    assert source_inventory.quantity == 50  # Started with 100, transferred 50

    # Verify target inventory was created
    target_inventory = Inventory.query.filter_by(
        product_id=sample_inventory.product_id,
        store_id='STORE-002'
    ).first()
    assert target_inventory is not None
    assert target_inventory.quantity == 50

def test_transfer_inventory_insufficient_stock(client, database, sample_inventory):
    transfer_data = {
        'product_id': sample_inventory.product_id,
        'source_store_id': sample_inventory.store_id,
        'target_store_id': 'STORE-002',
        'quantity': 150  # More than available (100)
    }
    
    response = client.post('/api/inventory/transfer',
                          data=json.dumps(transfer_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Insufficient stock in source store'

def test_transfer_inventory_missing_fields(client, database):
    transfer_data = {
        'product_id': 'some-id',
        'source_store_id': 'STORE-001'
        # Missing required fields
    }
    
    response = client.post('/api/inventory/transfer',
                          data=json.dumps(transfer_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Missing required fields'

def test_transfer_inventory_invalid_quantity(client, database, sample_inventory):
    transfer_data = {
        'product_id': sample_inventory.product_id,
        'source_store_id': sample_inventory.store_id,
        'target_store_id': 'STORE-002',
        'quantity': 0  # Invalid quantity
    }
    
    response = client.post('/api/inventory/transfer',
                          data=json.dumps(transfer_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Quantity must be positive'

def test_get_inventory_alerts_empty(client, database):
    response = client.get('/api/inventory/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

def test_get_inventory_alerts_with_data(client, database, sample_inventory):
    # Update inventory to trigger alert
    sample_inventory.quantity = 5  # Below min_stock (10)
    database.session.commit()

    response = client.get('/api/inventory/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['id'] == sample_inventory.id
    assert data[0]['missing_quantity'] == 5  # min_stock (10) - quantity (5)

def test_get_inventory_alerts_multiple(client, database, sample_product):
    # Create multiple inventory items with different alert states
    inventories = [
        Inventory(id='1', product_id=sample_product.id, store_id='STORE-001',
                 quantity=5, min_stock=10),  # Alert
        Inventory(id='2', product_id=sample_product.id, store_id='STORE-002',
                 quantity=15, min_stock=10),  # No alert
        Inventory(id='3', product_id=sample_product.id, store_id='STORE-003',
                 quantity=8, min_stock=20)  # Alert
    ]
    for inventory in inventories:
        database.session.add(inventory)
    database.session.commit()

    response = client.get('/api/inventory/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2  # Only items below min_stock
    assert any(item['store_id'] == 'STORE-001' for item in data)
    assert any(item['store_id'] == 'STORE-003' for item in data)
