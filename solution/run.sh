#!/bin/sh
# Create JSON file with environment variables for api
echo "{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}"

echo "{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}" > config.json

# Run data-loader.py
exec python data-loader/data_loader.py

# Start the Flask API
exec python api/app.py