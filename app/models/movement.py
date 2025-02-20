from app.main import db
from datetime import datetime
from enum import Enum

class MovementType(Enum):
    IN = 'IN'
    OUT = 'OUT'
    TRANSFER = 'TRANSFER'

class Movement(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('product.id'), nullable=False)
    source_store_id = db.Column(db.String(36))
    target_store_id = db.Column(db.String(36))
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.Enum(MovementType), nullable=False)

    product = db.relationship('Product', backref=db.backref('movements', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'source_store_id': self.source_store_id,
            'target_store_id': self.target_store_id,
            'quantity': self.quantity,
            'timestamp': self.timestamp.isoformat(),
            'type': self.type.value
        }
