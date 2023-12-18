#!/bin/sh
# Create JSON file with environment variables for API
config_json="{\"DB_HOST\": \"$DB_HOST\", \"DB_PORT\": \"$DB_PORT\", \"DB_USER\": \"$DB_USER\", \"DB_PASSWORD\": \"$DB_PASSWORD\", \"DB_NAME\": \"$DB_NAME\"}"

echo "$config_json"

echo "$config_json" > config.json
# wait a little longer beacause sometimes is building the database
sleep 5

# Run data-loader.py
if [ "$SKIP_LOAD_DATA" != "true" ]; then
    python data-loader/data_loader.py
    #python data-loader/profiler_data_loader.py
fi

if [ "$DEVELOP_SERVER" = "true" ]; then
    python api/app.py
else
    # Start the API with Gunicorn to run API on a WSGI server
    echo "$config_json" > api/config.json
    cd api
    gunicorn -w 4 -b 0.0.0.0:5000 'startup:start()'
fi

