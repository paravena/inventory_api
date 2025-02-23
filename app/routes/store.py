from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from app.models.product import Product
from app.models.inventory import Inventory
from app.main import db
from app.utils.logging_config import log_endpoint
from app.routes.inventory import inventory_model, inventory_create_model
import uuid

store_bp = Blueprint('store', __name__)
api = Namespace('store', description='Store operations')

error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error message')
})

@api.route('/<store_id>/inventory')
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
    @api.response(201, 'Inventory created successfully', inventory_model)
    @api.response(400, 'Validation Error', error_model)
    @api.response(404, 'Product not found', error_model)
    @log_endpoint
    def post(self, store_id):
        """Initialize store inventory for a product"""
        data = request.get_json()
        if not data:
            return {'error': 'No input data provided'}, 400

        # Validate request data
        try:
            if data['quantity'] <= 0:
                return {'error': 'Quantity must be greater than 0'}, 400
            if data['min_stock'] <= 0:
                return {'error': 'Minimum stock must be greater than 0'}, 400
        except (KeyError, TypeError):
            return {'error': 'Missing or invalid quantity or min_stock'}, 400

        # Check if product exists
        product = Product.query.get(data.get('product_id'))
        if not product:
            return {'error': 'Product not found'}, 404

        # Check if inventory already exists for this product and store
        existing_inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            store_id=store_id
        ).first()
        if existing_inventory:
            return {'error': 'Inventory already exists for this product in the store'}, 400

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
