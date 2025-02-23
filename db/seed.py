import os
import sys

# Add the repository root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app, db
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.movement import Movement
import uuid
import random
from datetime import datetime

# Sample data for pet products
DOG_PRODUCTS = [
    ("Premium Dog Food", "High-quality dry food for adult dogs", 29.99),
    ("Dog Collar", "Adjustable nylon collar with buckle", 12.99),
    ("Dog Leash", "Durable 6-foot leather leash", 19.99),
    ("Dog Bed", "Comfortable memory foam bed for medium-sized dogs", 49.99),
    ("Dog Toys Bundle", "Set of 5 durable chew toys", 24.99)
]

CAT_PRODUCTS = [
    ("Premium Cat Food", "Grain-free dry food for indoor cats", 27.99),
    ("Cat Litter Box", "Large covered litter box with filter", 34.99),
    ("Cat Tree", "Multi-level cat tree with scratching posts", 89.99),
    ("Cat Toys Set", "Interactive toys with catnip", 15.99),
    ("Cat Grooming Kit", "Complete grooming set for cats", 22.99)
]

STORE_IDS = [
    str(uuid.uuid4()),  # store 1
    str(uuid.uuid4()),  # store 2
    str(uuid.uuid4())   # store 3
]


def generate_sku(category, index):
    """Generate a unique SKU for a product"""
    return f"{category[:3].upper()}-{str(index).zfill(4)}"


def create_product(name, description, price, category):
    """Create a product with the given details"""
    return Product(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        category=category,
        price=price,
        sku=generate_sku(category, random.randint(1000, 9999))
    )


def create_inventory(product, store_id):
    """Create inventory record for a product"""
    return Inventory(
        id=str(uuid.uuid4()),
        product_id=product.id,
        store_id=store_id,
        quantity=random.randint(10, 100),
        min_stock=random.randint(5, 20)
    )


def seed_database():
    """Main function to seed the database with products and inventory"""
    app = create_app()
    with app.app_context():
        # Clear existing data in the correct order
        Movement.query.delete()
        db.session.commit()

        Inventory.query.delete()
        db.session.commit()

        Product.query.delete()
        db.session.commit()

        # Create products and inventory
        all_products = []

        # Create dog products
        for name, desc, price in DOG_PRODUCTS:
            product = create_product(name, desc, price, "Dogs")
            all_products.append(product)
            db.session.add(product)

        # Create cat products
        for name, desc, price in CAT_PRODUCTS:
            product = create_product(name, desc, price, "Cats")
            all_products.append(product)
            db.session.add(product)

        # Commit products
        db.session.commit()

        # Create inventory records
        for product in all_products:
            # Create inventory for each store
            for store_id in STORE_IDS:
                inventory = create_inventory(product, store_id)
                db.session.add(inventory)

        # Commit inventory records
        db.session.commit()

        print(f"Created {len(all_products)} products")
        print(f"Created {len(all_products) * len(STORE_IDS)} inventory records")


if __name__ == "__main__":
    seed_database()
