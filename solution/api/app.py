from flask import Flask
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from models.main import db
import json
import logging
from resources.doc import DocResource
from resources.genre import GenreResource
from resources.movie import MovieResource, MovieSingleResource


class MovieAPI:
    def __init__(self, connectionString):
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
        API_URL = '/docs/openapi.yaml'  # URL to your OpenAPI YAML content

        # Call factory function to create our blueprint
        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
            API_URL,
            config={  # Swagger UI config overrides
                'app_name': "Movie API"
            },
        )
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.app.register_blueprint(swaggerui_blueprint)
        self.setup_database(connectionString)
        self.setup_resources()

    def setup_database(self, connectionString):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
        self.db = db
        self.db.init_app(self.app)

    def setup_resources(self): # Add resources to the API

        self.api.add_resource(GenreResource, '/genres')
        self.api.add_resource(MovieResource, '/movies')
        self.api.add_resource(MovieSingleResource, '/movies/<string:movie_id>')
        self.api.add_resource(DocResource, '/docs/openapi.yaml')

    def start(self, debug = True, host='0.0.0.0', port=5000):
        self.app.run(debug=debug, host=host, port=port)
        return self.app


if __name__ == '__main__':
    with open('config.json') as config_file:
        config_data = json.load(config_file)

        # Use the config data to construct the db_params dictionary
        db_params = {
            "host": config_data["DB_HOST"],
            "port": int(config_data["DB_PORT"]),
            "user": config_data["DB_USER"],
            "password": config_data["DB_PASSWORD"],
            "database": config_data["DB_NAME"],
        }
        connectionString = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params)
        movie_api = MovieAPI(connectionString)
        movie_api.start()
