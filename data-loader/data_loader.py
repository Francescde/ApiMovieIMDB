from utils.data_transformer import DataTransformer
from utils.data_inserter import DataInserter
from utils.data_source import DataSource


class DataLoader:
    def __init__(self, db_params):
        self.data_transformer = DataTransformer()
        self.data_inserter = DataInserter(db_params)

    def etl_movies_genres(self, basics_ds, ratings_ds, akas_ds):
        try:
            self.truncate_tables(["movie_genres", "genres", "movies"])
            genres_movie_data = self.insert_movies_and_genres_rows_and_retrieve_relation(basics_ds, ratings_ds, akas_ds)
            movie_genres_data = self.data_transformer.get_movie_genres_data(genres_movie_data)
            self.data_inserter.execute_insert(movie_genres_data, "movie_genres")
            self.data_inserter.close_connection()
        except Exception as e:
            self.data_inserter.rollback()
            print(f"Error: {e}")

    def insert_movies_data_and_get_movie_genres_data(self, basics_ds, ratings_ds, akas_ds):
        movies_data, basics_df = self.data_transformer.get_movies_data(basics_ds, ratings_ds, akas_ds)
        self.data_inserter.execute_insert(movies_data, "movies")
        return basics_df

    def insert_movies_and_genres_rows_and_retrieve_relation(self, basics_ds, ratings_ds, akas_ds):
        movie_genres_df = self.insert_movies_data_and_get_movie_genres_data(basics_ds, ratings_ds, akas_ds)
        genres_data, genres_movie_data = self.data_transformer.get_genres_data(movie_genres_df)
        self.data_inserter.execute_insert(genres_data, "genres")
        return genres_movie_data

    def truncate_tables(self, table_names):
        for table in table_names:
            self.data_inserter.truncate_table(table)


# Usage
if __name__ == "__main__":
    db_params = {
        "host": "postgres",
        "port": 5432,
        "user": "your_user",
        "password": "your_password",
        "database": "your_database",
    }

    basics_ds = DataSource("https://datasets.imdbws.com/title.basics.tsv.gz", True)
    ratings_ds = DataSource("https://datasets.imdbws.com/title.ratings.tsv.gz", True)
    akas_ds = DataSource("https://datasets.imdbws.com/title.akas.tsv.gz", True)

    data_loader = DataLoader(db_params)
    data_loader.etl_movies_genres(basics_ds, ratings_ds, akas_ds)
