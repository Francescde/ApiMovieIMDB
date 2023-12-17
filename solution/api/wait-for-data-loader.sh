#!/bin/sh
data_loader_service="apimovieimdb-data-loader-1"
set -e


# Wait until the data-loader service container is active
echo "$(docker inspect -f '{{.State.Running}}' $data_loader_service)"
until [ "$(docker inspect -f '{{.State.Running}}' $data_loader_service)" = "false" ]; do
  echo "Waiting for data-loader service container to be done..."
  echo "$(docker inspect -f '{{.State.Running}}' $data_loader_service 2>/dev/null)"
  sleep 300
done

echo "Data-loader service container is done - executing command"
exec python app.py
