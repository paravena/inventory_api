from flask import Flask
from dotenv import load_dotenv
import os
from app.utils.logging_config import setup_logger
from app import db, api

# Load environment variables from .env file
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    # Initialize JSON logging
    setup_logger()

    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config.update(test_config)

    db.init_app(app)
    api.init_app(app)

    # Import routes
    from app.routes.inventory import inventory_bp, api as inventory_ns
    from app.routes.products import products_bp, api as products_ns
    from app.routes.store import store_bp, api as store_ns

    # Register blueprints and namespaces
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(store_bp, url_prefix='/api/stores')
    api.add_namespace(inventory_ns, path='/inventory')
    api.add_namespace(products_ns, path='/products')
    api.add_namespace(store_ns, path='/stores')

    return app


def init_db(app):
    with app.app_context():
        db.create_all()


app = create_app()
init_db(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
