import pandas as pd
import uuid
from sqlalchemy import create_engine, text
import requests
from io import BytesIO
import gzip


class DataSource:
    def __init__(self, source, downloadable):
        self.source = source
        self.downloadable = downloadable

    def download_and_extract(self):
        response = requests.get(self.source)
        with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as file:
            content = file.read()
        return content

    def download_df(self):
        content = self.download_and_extract()
        return pd.read_csv(BytesIO(content), sep='\t')

    def read(self):
        if self.downloadable:
            return self.download_df()
        return pd.read_csv(self.source, sep='\t')


class DataTransformer:
    def assign_non_nulls_titles(self, dataFrame, columnName, akas_data_source):
        akas_df = akas_data_source.read()
        filtered_df = akas_df.dropna(subset=['title'])
        null_title_df = dataFrame[dataFrame[columnName].isnull()]['tconst']
        filtered_df = pd.merge(null_title_df, filtered_df, how='left', left_on='tconst', right_on='titleId')
        filtered_df['isOriginalTitle'] = pd.to_numeric(filtered_df['isOriginalTitle'], errors='coerce').fillna(0)
        sorted_df = filtered_df.sort_values(by='isOriginalTitle', ascending=False)
        final_titles_df = sorted_df.drop_duplicates(subset='titleId', keep='first')[['titleId', 'title']]
        merged_df = pd.merge(dataFrame, final_titles_df, how='left', left_on='tconst', right_on='titleId')
        merged_df[columnName] = merged_df[columnName].fillna(merged_df['title'])
        return merged_df

    def get_basics_data(self, basics_df, akas_data_source):
        basics_df = basics_df[basics_df['titleType'] == 'movie']
        basics_df.loc[:, "movie_id"] = basics_df["tconst"].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_URL, x)))
        basics_df = basics_df.drop_duplicates(subset='tconst')
        basics_df.loc[:, "runtimeMinutesNumeric"] = basics_df["runtimeMinutes"].replace(r"\N", None)
        basics_df.loc[:, "startYearNumeric"] = basics_df["startYear"].replace(r"\N", None)
        basics_df = self.assign_non_nulls_titles(basics_df, "primaryTitle", akas_data_source)
        basics_df = basics_df.dropna(subset=['primaryTitle'])
        return basics_df

    def get_movies_data(self, basics_ds, ratings_ds, akas_data_source):
        basics_df = self.get_basics_data(basics_ds.read(), akas_data_source)

        movies_data = pd.merge(basics_df, ratings_ds.read(), on="tconst", how="left")
        movies_data["ratingNumeric"] = movies_data["averageRating"].replace(r"\N", None)
        movies_data = movies_data[
            ["movie_id", "primaryTitle", "startYearNumeric", "runtimeMinutesNumeric", "ratingNumeric"]]
        movies_data.columns = ["id", "title", "year", "runtime", "rating"]
        return movies_data, basics_df

    def get_genres_data(self, filtered_basics_df):
        genres_movie_data = filtered_basics_df[["movie_id", "genres"]]
        genres_movie_data["genres"] = genres_movie_data["genres"].apply(lambda x: x.split(','))
        genres_movie_data = genres_movie_data.explode("genres").dropna()
        genres_movie_data = genres_movie_data[genres_movie_data["genres"] != r"\N"]
        genres_movie_data["genre_id"] = genres_movie_data["genres"].apply(
            lambda x: str(uuid.uuid5(uuid.NAMESPACE_URL, x)))

        genres_data = genres_movie_data[["genre_id", "genres"]]
        genres_data.columns = ["id", "name"]
        genres_data = genres_data.drop_duplicates(subset='id')
        return genres_data, genres_movie_data

    def get_movie_genres_data(self, genres_movie_data):
        movie_genres_data = genres_movie_data[["movie_id", "genre_id"]]
        movie_genres_data.columns = ["movie_id", "genre_id"]
        return movie_genres_data


class DataInserter:
    def __init__(self, db_params):
        self.engine = create_engine(
            'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params))
        self.conn = self.engine.connect()

    def execute_insert(self, frame, table_name):
        print("inserting ", table_name)
        frame.to_sql(name=table_name, con=self.conn, if_exists='append', index=False, method="multi", chunksize=1000)

    def close_connection(self):
        self.conn.close()

    def truncate_table(self, table_name):
        # Truncate each table
        self.conn.execute(text(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;'))
        print(f'Table {table_name} truncated successfully.')


class DataLoader:
    def __init__(self, db_params):
        self.data_transformer = DataTransformer()
        self.data_inserter = DataInserter(db_params)

    def etl_movies_genres(self, basics_ds, ratings_ds, akas_ds):
        self.truncate_tables(["movie_genres", "genres", "movies"])
        genres_movie_data = self.insert_movies_and_genres_rows_and_retrieve_relation(basics_ds, ratings_ds, akas_ds)
        movie_genres_data = self.data_transformer.get_movie_genres_data(genres_movie_data)
        self.data_inserter.execute_insert(movie_genres_data, "movie_genres")
        self.data_inserter.close_connection()

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
    data_loader = DataLoader(db_params)

    basics_ds = DataSource("title.basics.tsv", False)
    ratings_ds = DataSource("title.ratings.tsv", False)
    akas_ds = DataSource("title.akas.tsv", False)

    data_loader.etl_movies_genres(basics_ds, ratings_ds, akas_ds)
