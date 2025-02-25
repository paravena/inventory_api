# Railway Deployment Guide

This guide will help you deploy the Inventory API to Railway.

## Prerequisites

1. Create a Railway account at https://railway.app/
2. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

## Deployment Steps

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Create a new project in Railway**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select this repository

3. **Add PostgreSQL Service**
   - In your Railway project dashboard
   - Click "New Service"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically create a PostgreSQL instance
   - The DATABASE_URL will be automatically added to your environment variables

4. **Configure Environment Variables**
   In your Railway project settings, add the following environment variables:
   ```
   FLASK_APP=app.main:app
   FLASK_ENV=production
   ```
   Note: Railway will automatically set the PORT variable.

5. **Deploy the Application**
   - Railway will automatically detect the Dockerfile and deploy your application
   - The deployment will use the configuration from railway.toml
   - You can monitor the deployment progress in the Railway dashboard

6. **Verify the Deployment**
   - Once deployed, Railway will provide you with a URL for your API
   - Test the health check endpoint by visiting `<your-railway-url>/health`
   - The API should return a JSON response with status "healthy"

## Troubleshooting

- If the deployment fails, check the logs in the Railway dashboard
- Ensure all environment variables are properly set
- Verify that the PostgreSQL connection is working
- Check if the health check endpoint is responding

## Monitoring

- Use the Railway dashboard to monitor your application
- Check logs for any errors
- Monitor PostgreSQL database metrics

## Additional Notes

- The application uses Gunicorn as the production server
- Railway will automatically handle HTTPS/SSL
- The application will restart automatically on failure (configured in railway.toml)
- Database backups are handled automatically by Railway
