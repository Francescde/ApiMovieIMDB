import json

from data_loader import DataLoader
from utils.data_source import DataSource
import cProfile

if __name__ == "__main__":
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

        basics_ds = DataSource("https://datasets.imdbws.com/title.basics.tsv.gz", True)
        ratings_ds = DataSource("https://datasets.imdbws.com/title.ratings.tsv.gz", True)
        akas_ds = None #DataSource("https://datasets.imdbws.com/title.akas.tsv.gz", True)

        data_loader = DataLoader(db_params)
        cProfile.run('data_loader.etl_movies_genres(basics_ds, ratings_ds, akas_ds)')
