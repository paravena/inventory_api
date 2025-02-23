# API Setup Guide

## Prerequisites

Before setting up the Inventory Management API, ensure you have the following installed:

- Docker and Docker Compose installed on your system
- Python 3.8 or higher
- pip (Python package manager)

## Environment Setup

1. Clone the repository to your local machine.

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   POSTGRES_DB=inventory
   POSTGRES_USER=inventory_user
   POSTGRES_PASSWORD=your_password
   DATABASE_URL=postgresql://inventory_user:your_password@localhost:5432/inventory
   FLASK_APP=app.main:app
   FLASK_ENV=development
   FLASK_RUN_PORT=3000
   ```

## Installation Steps

1. Activate your virtual environment:
   ```bash
   # On Unix/macOS
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the PostgreSQL database:
   ```bash
   docker-compose up -d
   ```

4. Run the application:
   ```bash
   flask run
   ```

The API will be available at `http://localhost:3000`
Swagger documentation can be accessed at `http://localhost:3000/api/docs`

## Development Setup

For development purposes, you might want to:

1. Enable debug mode by setting `FLASK_ENV=development` in your `.env` file
2. Use Flask's debug mode with auto-reload:
   ```bash
   flask run --debug
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL container is running: `docker ps`
   - Check database logs: `docker-compose logs db`
   - Ensure database credentials in `.env` match docker-compose.yml

2. **Port Conflicts**
   - If port 3000 is in use, modify `FLASK_RUN_PORT` in `.env`
   - For PostgreSQL port conflicts, modify the port mapping in docker-compose.yml

3. **Virtual Environment Issues**
   - Ensure virtual environment is activated
   - Verify Python version matches requirements
   - Try removing and recreating the virtual environment

## Production Deployment Considerations

1. Set appropriate environment variables:
   - Set `FLASK_ENV=production`
   - Use strong, unique passwords
   - Configure proper logging

2. Security measures:
   - Enable HTTPS
   - Set up proper firewalls
   - Configure rate limiting

3. Performance optimization:
   - Configure proper database connection pooling
   - Set up appropriate worker processes
   - Consider using a production-grade WSGI server like Gunicorn
