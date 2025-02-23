from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

# Initialize extensions
db = SQLAlchemy()
api = Api(
    title='Inventory API',
    version='1.0',
    description='A simple inventory management API',
    doc='/api/docs',
    prefix='/api'
)

# Import create_app function
from app.main import create_app
