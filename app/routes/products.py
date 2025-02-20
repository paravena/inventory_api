from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from app.models.product import Product
from app.models.inventory import Inventory
from app.main import db
from app.utils.logging_config import log_endpoint
import uuid

products_bp = Blueprint('api/products', __name__)
api = Namespace('api/products', description='Product operations')

# Define models for swagger documentation
product_model = api.model('Product', {
    'id': fields.String(readonly=True, description='Product unique identifier'),
    'name': fields.String(required=True, description='Product name'),
    'description': fields.String(description='Product description'),
    'category': fields.String(required=True, description='Product category'),
    'price': fields.Float(required=True, description='Product price'),
    'sku': fields.String(required=True, description='Product SKU')
})

product_list_model = api.model('ProductList', {
    'items': fields.List(fields.Nested(product_model)),
    'total': fields.Integer,
    'pages': fields.Integer,
    'current_page': fields.Integer
})

@api.route('/')
class ProductList(Resource):
    @api.doc('list_products',
             params={
                 'page': {'description': 'Page number', 'type': 'integer', 'default': 1},
                 'per_page': {'description': 'Items per page', 'type': 'integer', 'default': 10},
                 'category': {'description': 'Filter by category'},
                 'min_price': {'description': 'Minimum price', 'type': 'number'},
                 'max_price': {'description': 'Maximum price', 'type': 'number'},
                 'min_stock': {'description': 'Minimum stock level', 'type': 'integer'}
             })
    @api.marshal_with(product_list_model)
    @log_endpoint
    def get(self):
        """List all products with optional filters"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_stock = request.args.get('min_stock', type=int)

        query = Product.query

        if category:
            query = query.filter(Product.category == category)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if min_stock is not None:
            query = query.join(Inventory).group_by(Product.id).having(db.func.sum(Inventory.quantity) >= min_stock)

        pagination = query.paginate(page=page, per_page=per_page)

        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }

    @api.doc('create_product')
    @api.expect(product_model)
    @api.marshal_with(product_model, code=201)
    @api.response(400, 'Validation Error')
    @log_endpoint
    def post(self):
        """Create a new product"""
        data = request.get_json()

        required_fields = ['name', 'category', 'price', 'sku']
        for field in required_fields:
            if field not in data:
                api.abort(400, f'Missing required field: {field}')

        if Product.query.filter_by(sku=data['sku']).first():
            api.abort(400, 'SKU already exists')

        product = Product(
            id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            price=data['price'],
            sku=data['sku']
        )

        db.session.add(product)
        db.session.commit()

        return product.to_dict(), 201

@api.route('/<id>')
@api.param('id', 'The product identifier')
class ProductItem(Resource):
    @api.doc('get_product')
    @api.marshal_with(product_model)
    @api.response(404, 'Product not found')
    @log_endpoint
    def get(self, id):
        """Get a product by ID"""
        product = Product.query.get_or_404(id)
        return product.to_dict()

    @api.doc('update_product')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    @api.response(400, 'Validation Error')
    @api.response(404, 'Product not found')
    @log_endpoint
    def put(self, id):
        """Update a product"""
        product = Product.query.get_or_404(id)
        data = request.get_json()

        if 'sku' in data and data['sku'] != product.sku:
            if Product.query.filter_by(sku=data['sku']).first():
                api.abort(400, 'SKU already exists')

        for field in ['name', 'description', 'category', 'price', 'sku']:
            if field in data:
                setattr(product, field, data[field])

        db.session.commit()
        return product.to_dict()

    @api.doc('delete_product')
    @api.response(204, 'Product deleted')
    @api.response(400, 'Cannot delete product with inventory')
    @api.response(404, 'Product not found')
    @log_endpoint
    def delete(self, id):
        """Delete a product"""
        product = Product.query.get_or_404(id)

        if product.inventory_items:
            api.abort(400, 'Cannot delete product with existing inventory')

        db.session.delete(product)
        db.session.commit()
        return '', 204
