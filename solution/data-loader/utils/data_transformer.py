import uuid

import pandas as pd
import numpy as np


class DataTransformer:
    def get_movies_data(self, basics_ds, ratings_ds, akas_data_source):
        basics_df = self.get_basics_data(basics_ds.read(), akas_data_source)

        movies_data = pd.merge(basics_df, ratings_ds.read(), on="tconst", how="left")
        movies_data["ratingNumeric"] = pd.to_numeric(movies_data["averageRating"], errors='coerce')
        movies_data["ratingNumeric"] = movies_data["ratingNumeric"].replace({np.nan: None})
        movies_data = movies_data[
            ["movie_id", "primaryTitle", "startYearNumeric", "runtimeMinutesNumeric", "ratingNumeric", "imdb_link"]]
        movies_data.columns = ["id", "title", "year", "runtime", "rating", "imdb_link"]
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

    def get_basics_data(self, basics_df, akas_data_source):
        basics_df = basics_df[basics_df['titleType'] == 'movie']
        basics_df = basics_df.drop_duplicates(subset='tconst')
        basics_df.loc[:, "imdb_link"] = basics_df["tconst"].apply(
            lambda movie_id: f"https://www.imdb.com/title/{movie_id}/")
        basics_df.loc[:, "movie_id"] = basics_df["tconst"].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_URL, x)))
        basics_df.loc[:, "runtimeMinutesNumeric"] = pd.to_numeric(basics_df["runtimeMinutes"], errors='coerce')
        basics_df["runtimeMinutesNumeric"] = basics_df["runtimeMinutesNumeric"].replace({np.nan: None})
        basics_df.loc[:, "startYearNumeric"] = pd.to_numeric(basics_df["startYear"], errors='coerce')
        basics_df["startYear"] = basics_df["startYear"].replace({np.nan: None})
        if akas_data_source:
            basics_df = self.assign_non_nulls_titles(basics_df, "primaryTitle", akas_data_source)
        all_basics = len(basics_df['primaryTitle'])
        basics_df = basics_df.dropna(subset=['primaryTitle'])
        new_all_basics = len(basics_df['primaryTitle'])
        # Print the number of filled rows
        print(f'Droped {all_basics - new_all_basics} rows from {all_basics}')
        return basics_df

    def assign_non_nulls_titles(self, dataFrame, columnName, akas_data_source):
        akas_df = akas_data_source.read()
        filtered_df = akas_df.dropna(subset=['title'])

        # Get the tconst values for null titles
        null_title_tconsts = dataFrame[dataFrame[columnName].isnull()]['tconst']
        # Use isin to filter the rows in filtered_df with the null_title_tconsts
        filtered_df = filtered_df[filtered_df['titleId'].isin(null_title_tconsts)]

        filtered_df['isOriginalTitle'] = pd.to_numeric(filtered_df['isOriginalTitle'], errors='coerce').fillna(0)
        sorted_df = filtered_df.sort_values(by='isOriginalTitle', ascending=False)
        final_titles_df = sorted_df.drop_duplicates(subset='titleId', keep='first')[['titleId', 'title']]

        # Merge with dataFrame based on tconst
        merged_df = pd.merge(dataFrame, final_titles_df, how='left', left_on='tconst', right_on='titleId')

        # Use np.where to fill null values in columnName with 'title'
        merged_df[columnName] = np.where(merged_df[columnName].isnull(), merged_df['title'], merged_df[columnName])

        # Get the tconst values for still null titles after the merge
        still_null_title_tconsts = len(merged_df[merged_df[columnName].isnull()][columnName])

        # Print the number of filled rows
        print(f'Filled {len(null_title_tconsts) - still_null_title_tconsts} rows from {len(null_title_tconsts)}')

        return merged_df.dropna(subset=[columnName])
