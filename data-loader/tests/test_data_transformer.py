import unittest
import pandas as pd
from unittest.mock import MagicMock
from load_data import DataTransformer, DataSource


class TestDataTransformer(unittest.TestCase):

    def setUp(self):
        # Mocking the DataSource for testing
        self.akas_data_source = DataSource("mock_akas_source", downloadable=True)
        self.akas_data_source.read = MagicMock(return_value=pd.DataFrame({
            'titleId': ['1', '2', '3', '1'],
            'title': ['Movie12', 'Movie2', 'Movie3', 'Movie1'],
            'isOriginalTitle': [0, None, 0, 1]
        }))
        self.basics_df = pd.DataFrame({
            'tconst': ['1', '2', '3'],
            'titleType': ['movie', 'movie', 'tvSeries'],
            'runtimeMinutes': ['120', '\\N', '90'],
            'startYear': ['2000', '\\N', '1995'],
            'primaryTitle': ['Movie1', 'Movie2', 'TVSeries1']
        })
        self.basics_ds = DataSource("mock_basics_source", downloadable=True)
        self.basics_ds.read = MagicMock(return_value=self.basics_df)

        self.ratings_df = pd.DataFrame({
            'tconst': ['1', '2', '3'],
            'averageRating': ['8.0', '\\N', '7.5']
        })
        self.ratings_ds = DataSource("mock_ratings_source", downloadable=True)
        self.ratings_ds.read = MagicMock(return_value=self.ratings_df)

    def test_assign_non_nulls_titles(self):
        transformer = DataTransformer()
        df = pd.DataFrame({
            'tconst': ['1', '2', '3'],
            'columnName': [None, None, 'Movie3']
        })

        result_df = transformer.assign_non_nulls_titles(df, 'columnName', self.akas_data_source)

        # Add your assertions based on the expected behavior of assign_non_nulls_titles
        # For example:
        self.assertEqual(result_df['columnName'].tolist(), ['Movie1', 'Movie2', 'Movie3'])

    def test_get_basics_data(self):
        transformer = DataTransformer()
        result_df = transformer.get_basics_data(self.basics_ds.read(), self.akas_data_source)

        # Add your assertions based on the expected behavior of get_basics_data
        # For example:
        self.assertEqual(result_df['runtimeMinutesNumeric'].tolist(), ['120', None])

    def test_get_movies_data(self):
        transformer = DataTransformer()
        movies_data, basics_df = transformer.get_movies_data(self.basics_ds, self.ratings_ds, self.akas_data_source)

        # Add your assertions based on the expected behavior of get_movies_data
        # For example:
        self.assertEqual(movies_data['rating'].tolist(), ['8.0', None])

    def test_get_genres_data(self):
        transformer = DataTransformer()
        filtered_basics_df = pd.DataFrame({
            'movie_id': ['1', '2', '3'],
            'genres': ['Action', 'Drama', 'Action,Comedy']
        })
        genres_data, genres_movie_data = transformer.get_genres_data(filtered_basics_df)

        # Add your assertions based on the expected behavior of get_genres_data
        # For example:
        self.assertEqual(genres_data['name'].tolist(), ['Action', 'Drama', 'Comedy'])

    def test_get_movie_genres_data(self):
        transformer = DataTransformer()
        genres_movie_data = pd.DataFrame({
            'movie_id': ['1', '2', '3'],
            'genre_id': ['101', '102', '103']
        })
        result_df = transformer.get_movie_genres_data(genres_movie_data)

        # Add your assertions based on the expected behavior of get_movie_genres_data
        # For example:
        self.assertEqual(result_df['genre_id'].tolist(), ['101', '102', '103'])

if __name__ == '__main__':
    unittest.main()
