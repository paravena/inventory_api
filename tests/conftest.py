import pytest
import os
import tempfile
from app.main import db, create_app, init_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.movement import Movement, MovementType
import uuid

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    app = create_app(test_config)
    init_db(app)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

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

@pytest.fixture
def sample_inventory(database, sample_product):
    inventory = Inventory(
        id=str(uuid.uuid4()),
        product_id=sample_product.id,
        store_id='STORE-001',
        quantity=100,
        min_stock=10
    )
    database.session.add(inventory)
    database.session.commit()
    return inventory

@pytest.fixture
def sample_movement(database, sample_product):
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
    return movement
