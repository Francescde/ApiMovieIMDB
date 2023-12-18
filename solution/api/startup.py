import json

from app import MovieAPI

def start():
    with open('config.json') as config_file:
        # Use the config data to construct the db_params dictionary
        config_data = json.load(config_file)
        db_params = {
            "host": config_data["DB_HOST"],
            "port": int(config_data["DB_PORT"]),
            "user": config_data["DB_USER"],
            "password": config_data["DB_PASSWORD"],
            "database": config_data["DB_NAME"],
        }
        connectionString = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params)
        movie_api = MovieAPI(connectionString)
        return movie_api.app

