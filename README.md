# Inventory Management API

A robust RESTful API for managing product inventory across multiple stores, built with Flask and PostgreSQL.

## Overview

This API provides a comprehensive solution for inventory management, featuring:
- Product management (CRUD operations)
- Store-specific inventory tracking
- Inter-store inventory transfers
- Low stock alerts
- Detailed movement history

## Documentation

Detailed documentation is available in the `docs` folder:

- [API Documentation](docs/api-documentation.md) - Complete API reference with endpoints, parameters, and examples
- [Setup Guide](docs/api-setup.md) - Detailed installation and configuration instructions
- [Testing Guide](docs/testing-guide.md) - Instructions for running and writing tests
- [Design Decisions](docs/design-decisions.md) - Architecture and implementation details

## Quick Start

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   POSTGRES_DB=inventory
   POSTGRES_USER=inventory_user
   POSTGRES_PASSWORD=your_password
   DATABASE_URL=postgresql://inventory_user:your_password@localhost:5432/inventory
   FLASK_APP=app.main:app
   FLASK_ENV=development
   FLASK_RUN_PORT=3000
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Start the database: `docker-compose up -d`
5. (Optional) Seed the database with sample data: `python db/seed.py`
6. Run the application: `flask run`

The API will be available at `http://localhost:3000`
Swagger documentation can be accessed at `http://localhost:3000/api/docs`

## Deployment to Railway

This application is configured for deployment on Railway. Follow these steps to deploy:

1. Create a Railway account and install the Railway CLI
2. Fork or clone this repository
3. Create a new project in Railway and connect it to your repository
4. Add a PostgreSQL database to your Railway project
5. Configure the following environment variables in Railway:
   ```
   DATABASE_URL - (Railway will automatically set this)
   FLASK_APP=app.main:app
   FLASK_ENV=production
   ```
6. Deploy your application:
   - Railway will automatically detect the Python project
   - It will use the Procfile for deployment configuration
   - The database will be automatically configured using Railway's PostgreSQL add-on

### Important Notes
- The application will automatically use the `DATABASE_URL` provided by Railway
- The Procfile is configured to use gunicorn with 4 workers
- Python 3.9.21 is specified in runtime.txt
- Make sure all environment variables are properly set in Railway's dashboard

## License

This project is licensed under the MIT License.
