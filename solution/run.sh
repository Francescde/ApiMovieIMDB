#!/bin/sh
# Create JSON file with environment variables for api
echo "{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}"

echo "{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}" > config.json

# Run data-loader.py
python data-loader/data_loader.py
#developer service
python api/app.py


# Start the API with Gunicorn to run api on a WSGI server
#echo "{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}" > api/config.json
#cd api
#gunicorn -w 4 -b 0.0.0.0:5000 startup:start
