from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from app.models.inventory import Inventory
from app.models.movement import Movement, MovementType
from app.main import db
from app.utils.logging_config import log_endpoint
import uuid

inventory_bp = Blueprint('inventory', __name__)
api = Namespace('inventory', description='Inventory operations')

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

error_model = api.model('Error', {
    'message': fields.String(required=True, description='Error message')
})


@api.route('/transfer')
class InventoryTransfer(Resource):
    @api.doc('transfer_inventory')
    @api.expect(transfer_request_model)
    @api.response(201, 'Transfer successful', movement_model)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Source inventory not found', error_model)
    @log_endpoint
    def post(self):
        """Transfer inventory between stores"""
        data = request.get_json()
        if not data:
            return {'error': 'No input data provided'}, 400

        required_fields = ['product_id', 'source_store_id', 'target_store_id', 'quantity']
        if not all(field in data for field in required_fields):
            return {'error': 'Missing required fields'}, 400

        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                return {'error': 'Quantity must be positive'}, 400
        except (ValueError, TypeError):
            return {'error': 'Invalid quantity value'}, 400

        # Check source inventory
        source_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=data['source_store_id']
        ).first()

        if not source_inventory:
            return {'error': 'Source inventory not found'}, 404

        if source_inventory.quantity < data['quantity']:
            return {'error': 'Insufficient stock in source store'}, 400

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

        return api.marshal(movement.to_dict(), movement_model), 201


@api.route('/stores/<store_id>/inventory')
@api.param('store_id', 'The store identifier')
class StoreInventoryCreate(Resource):
    @api.doc('create_store_inventory')
    @api.expect(inventory_create_model)
    @api.response(201, 'Inventory created successfully', inventory_model)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Product not found', error_model)
    @log_endpoint
    def post(self, store_id):
        """Initialize store inventory for a product"""
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        try:
            if data['quantity'] <= 0:
                return {'message': 'Quantity must be greater than 0'}, 400
            if data['min_stock'] <= 0:
                return {'message': 'Minimum stock must be greater than 0'}, 400
        except (KeyError, TypeError):
            return {'message': 'Missing or invalid quantity or min_stock'}, 400

        # Check if product exists
        from app.models.product import Product
        product = Product.query.get(data.get('product_id'))
        if not product:
            return {'message': 'Product not found'}, 404

        # Check if inventory already exists for this product and store
        existing_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=store_id
        ).first()
        if existing_inventory:
            return {'message': 'Inventory already exists for this product in the store'}, 400

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

        result = inventory.to_dict()
        result['product'] = product.to_dict()
        return api.marshal(result, inventory_model), 201


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
