import pytest
from datetime import datetime
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.movement import Movement, MovementType
import uuid

def test_product_creation(database):
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

    saved_product = Product.query.get(product.id)
    assert saved_product is not None
    assert saved_product.name == 'Test Product'
    assert float(saved_product.price) == 10.99
    assert isinstance(saved_product.created_at, datetime)
    assert isinstance(saved_product.updated_at, datetime)

def test_product_to_dict(database):
    product = Product(
        id='test-id',
        name='Test Product',
        description='Test Description',
        category='Test Category',
        price=10.99,
        sku='TEST-SKU-001'
    )
    database.session.add(product)
    database.session.commit()

    product_dict = product.to_dict()
    assert product_dict['id'] == 'test-id'
    assert product_dict['name'] == 'Test Product'
    assert product_dict['description'] == 'Test Description'
    assert product_dict['category'] == 'Test Category'
    assert product_dict['price'] == 10.99
    assert product_dict['sku'] == 'TEST-SKU-001'
    assert 'created_at' in product_dict
    assert 'updated_at' in product_dict

def test_inventory_creation(database, sample_product):
    inventory = Inventory(
        id=str(uuid.uuid4()),
        product_id=sample_product.id,
        store_id='STORE-001',
        quantity=100,
        min_stock=10
    )
    database.session.add(inventory)
    database.session.commit()

    saved_inventory = Inventory.query.get(inventory.id)
    assert saved_inventory is not None
    assert saved_inventory.product_id == sample_product.id
    assert saved_inventory.quantity == 100
    assert saved_inventory.min_stock == 10
    assert isinstance(saved_inventory.created_at, datetime)
    assert isinstance(saved_inventory.updated_at, datetime)

def test_inventory_to_dict(database, sample_product):
    inventory = Inventory(
        id='test-id',
        product_id=sample_product.id,
        store_id='STORE-001',
        quantity=100,
        min_stock=10
    )
    database.session.add(inventory)
    database.session.commit()

    inventory_dict = inventory.to_dict()
    assert inventory_dict['id'] == 'test-id'
    assert inventory_dict['product_id'] == sample_product.id
    assert inventory_dict['store_id'] == 'STORE-001'
    assert inventory_dict['quantity'] == 100
    assert inventory_dict['min_stock'] == 10
    assert 'created_at' in inventory_dict
    assert 'updated_at' in inventory_dict

def test_inventory_product_relationship(database, sample_product):
    inventory = Inventory(
        id=str(uuid.uuid4()),
        product_id=sample_product.id,
        store_id='STORE-001',
        quantity=100,
        min_stock=10
    )
    database.session.add(inventory)
    database.session.commit()

    # Test inventory.product relationship
    assert inventory.product == sample_product
    # Test product.inventory_items relationship
    assert len(sample_product.inventory_items) == 1
    assert sample_product.inventory_items[0] == inventory

def test_movement_creation(database, sample_product):
    movement = Movement(
        id=str(uuid.uuid4()),
        product_id=sample_product.id,
        source_store_id='STORE-001',
        target_store_id='STORE-002',
        quantity=50,
        type=MovementType.TRANSFER
    )
    database.session.add(movement)
    database.session.commit()

    saved_movement = Movement.query.get(movement.id)
    assert saved_movement is not None
    assert saved_movement.product_id == sample_product.id
    assert saved_movement.quantity == 50
    assert saved_movement.type == MovementType.TRANSFER
    assert isinstance(saved_movement.timestamp, datetime)

def test_movement_to_dict(database, sample_product):
    movement = Movement(
        id='test-id',
        product_id=sample_product.id,
        source_store_id='STORE-001',
        target_store_id='STORE-002',
        quantity=50,
        type=MovementType.TRANSFER
    )
    database.session.add(movement)
    database.session.commit()

    movement_dict = movement.to_dict()
    assert movement_dict['id'] == 'test-id'
    assert movement_dict['product_id'] == sample_product.id
    assert movement_dict['source_store_id'] == 'STORE-001'
    assert movement_dict['target_store_id'] == 'STORE-002'
    assert movement_dict['quantity'] == 50
    assert movement_dict['type'] == MovementType.TRANSFER.value
    assert 'timestamp' in movement_dict

def test_movement_product_relationship(database, sample_product):
    movement = Movement(
        id=str(uuid.uuid4()),
        product_id=sample_product.id,
        source_store_id='STORE-001',
        target_store_id='STORE-002',
        quantity=50,
        type=MovementType.TRANSFER
    )
    database.session.add(movement)
    database.session.commit()

    # Test movement.product relationship
    assert movement.product == sample_product
    # Test product.movements relationship
    assert len(sample_product.movements) == 1
    assert sample_product.movements[0] == movement

def test_movement_type_enum():
    assert MovementType.IN.value == 'IN'
    assert MovementType.OUT.value == 'OUT'
    assert MovementType.TRANSFER.value == 'TRANSFER'
