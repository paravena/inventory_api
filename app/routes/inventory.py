from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from app.models.inventory import Inventory
from app.models.movement import Movement, MovementType
from app.models.product import Product
from app.main import db
from app.utils.logging_config import log_endpoint
import uuid
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)
api = Namespace('api/inventory', description='Inventory operations')

# Define models for swagger documentation
product_model = api.model('ProductInInventory', {
    'id': fields.String(readonly=True, description='Product unique identifier'),
    'name': fields.String(description='Product name'),
    'sku': fields.String(description='Product SKU')
})

inventory_model = api.model('Inventory', {
    'id': fields.String(readonly=True, description='Inventory unique identifier'),
    'product_id': fields.String(description='Product ID'),
    'store_id': fields.String(description='Store ID'),
    'quantity': fields.Integer(description='Current quantity'),
    'min_stock': fields.Integer(description='Minimum stock level'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'product': fields.Nested(product_model)
})

transfer_request_model = api.model('TransferRequest', {
    'product_id': fields.String(required=True, description='Product ID to transfer'),
    'source_store_id': fields.String(required=True, description='Source store ID'),
    'target_store_id': fields.String(required=True, description='Target store ID'),
    'quantity': fields.Integer(required=True, description='Quantity to transfer')
})

movement_model = api.model('Movement', {
    'id': fields.String(readonly=True, description='Movement unique identifier'),
    'product_id': fields.String(description='Product ID'),
    'source_store_id': fields.String(description='Source store ID'),
    'target_store_id': fields.String(description='Target store ID'),
    'quantity': fields.Integer(description='Quantity transferred'),
    'type': fields.String(description='Movement type (IN, OUT, TRANSFER)', enum=['IN', 'OUT', 'TRANSFER']),
    'timestamp': fields.DateTime(description='Movement timestamp')
})

inventory_alert_model = api.model('InventoryAlert', {
    'id': fields.String(description='Inventory unique identifier'),
    'product_id': fields.String(description='Product ID'),
    'store_id': fields.String(description='Store ID'),
    'quantity': fields.Integer(description='Current quantity'),
    'min_stock': fields.Integer(description='Minimum stock level'),
    'product': fields.Nested(product_model),
    'missing_quantity': fields.Integer(description='Quantity needed to reach minimum stock')
})

inventory_create_model = api.model('InventoryCreate', {
    'product_id': fields.String(required=True, description='Product ID'),
    'quantity': fields.Integer(required=True, description='Initial quantity'),
    'min_stock': fields.Integer(required=True, description='Minimum stock level')
})

@api.route('/stores/<store_id>/inventory')
@api.param('store_id', 'The store identifier')
class StoreInventory(Resource):
    @api.doc('get_store_inventory')
    @api.marshal_list_with(inventory_model)
    @log_endpoint
    def get(self, store_id):
        """Get inventory for a specific store"""
        inventory = Inventory.query.filter_by(store_id=store_id).all()
        return [{
            **item.to_dict(),
            'product': item.product.to_dict()
        } for item in inventory]

    @api.doc('create_store_inventory')
    @api.expect(inventory_create_model)
    @api.marshal_with(inventory_model, code=201)
    @api.response(400, 'Validation Error')
    @api.response(404, 'Product not found')
    @log_endpoint
    def post(self, store_id):
        """Initialize store inventory for a product"""
        data = request.get_json()

        # Validate request data
        if data['quantity'] <= 0:
            api.abort(400, 'Quantity must be greater than 0')
        if data['min_stock'] <= 0:
            api.abort(400, 'Minimum stock must be greater than 0')

        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            api.abort(404, 'Product not found')

        # Check if inventory already exists for this product and store
        existing_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=store_id
        ).first()
        if existing_inventory:
            api.abort(400, 'Inventory already exists for this product in the store')

        # Create new inventory
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=data['product_id'],
            store_id=store_id,
            quantity=data['quantity'],
            min_stock=data['min_stock']
        )

        db.session.add(inventory)
        db.session.commit()

        return {
            **inventory.to_dict(),
            'product': product.to_dict()
        }, 201

@api.route('/transfer')
class InventoryTransfer(Resource):
    @api.doc('transfer_inventory')
    @api.expect(transfer_request_model)
    @api.marshal_with(movement_model, code=201)
    @api.response(400, 'Validation Error')
    @log_endpoint
    def post(self):
        """Transfer inventory between stores"""
        data = request.get_json()

        required_fields = ['product_id', 'source_store_id', 'target_store_id', 'quantity']
        if not all(field in data for field in required_fields):
            api.abort(400, 'Missing required fields')

        if data['quantity'] <= 0:
            api.abort(400, 'Quantity must be positive')

        # Check source inventory
        source_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=data['source_store_id']
        ).first()

        if not source_inventory or source_inventory.quantity < data['quantity']:
            api.abort(400, 'Insufficient stock in source store')

        # Get or create target inventory
        target_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=data['target_store_id']
        ).first()

        if not target_inventory:
            target_inventory = Inventory(
                id=str(uuid.uuid4()),
                product_id=data['product_id'],
                store_id=data['target_store_id'],
                quantity=0,
                min_stock=0
            )
            db.session.add(target_inventory)

        # Create movement record
        movement = Movement(
            id=str(uuid.uuid4()),
            product_id=data['product_id'],
            source_store_id=data['source_store_id'],
            target_store_id=data['target_store_id'],
            quantity=data['quantity'],
            type=MovementType.TRANSFER
        )

        # Update inventories
        source_inventory.quantity -= data['quantity']
        target_inventory.quantity += data['quantity']

        db.session.add(movement)
        db.session.commit()

        return movement.to_dict(), 201

@api.route('/alerts')
class InventoryAlerts(Resource):
    @api.doc('get_inventory_alerts')
    @api.marshal_list_with(inventory_alert_model)
    @log_endpoint
    def get(self):
        """Get alerts for inventory items below minimum stock level"""
        alerts = Inventory.query.filter(
            Inventory.quantity <= Inventory.min_stock
        ).all()

        return [{
            **item.to_dict(),
            'product': item.product.to_dict(),
            'missing_quantity': item.min_stock - item.quantity
        } for item in alerts]
