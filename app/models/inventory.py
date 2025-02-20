from app.main import db
from datetime import datetime
from app.models.product import Product

class Inventory(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('product.id'), nullable=False)
    store_id = db.Column(db.String(36), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('inventory_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'store_id': self.store_id,
            'quantity': self.quantity,
            'min_stock': self.min_stock,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
