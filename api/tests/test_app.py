import unittest
from flask_testing import TestCase
from flask import Flask
from models.main import db, Movie, Genre
from app import MovieAPI

class TestMovieAPI(TestCase):
    def create_app(self):
        # Use an in-memory SQLite database for testing
        movieApi = MovieAPI('sqlite:///:memory:')
        app = movieApi.app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        return app

    def setUp(self):
        # Create tables in the in-memory database before each test
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Drop tables in the in-memory database after each test
        with self.app.app_context():
            db.drop_all()

    def test_movie_creation(self):
        # Test creating a new movie via the API
        client = self.app.test_client()
        response = client.post('/movies', json={
            'title': 'Test Movie',
            'year': 2022,
            'rating': 8.0,
            'runtime': 120,
            'imdb_link': 'https://www.imdb.com/test_movie'
        })
        self.assertEqual(response.status_code, 201)

        # Check if the movie is present in the database
        with self.app.app_context():
            movie = Movie.query.filter_by(title='Test Movie').first()
            self.assertIsNotNone(movie)
            self.assertEqual(movie.title, 'Test Movie')
            self.assertEqual(movie.year, 2022)
            self.assertEqual(movie.rating, 8.0)
            self.assertEqual(movie.runtime, 120)
            self.assertEqual(movie.imdb_link, 'https://www.imdb.com/test_movie')

    def test_genre_list(self):
        # Test listing genres via the API
        with self.app.app_context():
            # Create a test genre in the database
            test_genre = Genre(name='Test Genre')
            db.session.add(test_genre)
            db.session.commit()
            client = self.app.test_client()
            response = client.get('/genres')
            self.assertEqual(response.status_code, 200)

            # Check if the test genre is present in the response
            data = response.get_json()
            self.assertTrue(any(genre['name'] == 'Test Genre' for genre in data))

    def test_get_all_movies(self):
        # Test retrieving all movies via the API
        with self.app.app_context():
            movie1 = Movie(title='Movie 1', year=2020, rating=7.5, runtime=110)
            movie2 = Movie(title='Movie 2', year=2021, rating=8.0, runtime=120)
            db.session.add_all([movie1, movie2])
            db.session.commit()

            response = self.client.get('/movies')
            self.assertEqual(response.status_code, 200)

            # Check if the response contains the added movies
            data = response.json
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['title'], 'Movie 1')
            self.assertEqual(data[1]['title'], 'Movie 2')

    def test_get_single_movie(self):
        # Test retrieving a single movie by its ID via the API
        with self.app.app_context():
            movie = Movie(title='Test Movie', year=2022, rating=8.0, runtime=120)
            db.session.add(movie)
            db.session.commit()

            response = self.client.get(f'/movies/{movie.id}')
            self.assertEqual(response.status_code, 200)

            # Check if the response contains the correct movie
            data = response.json
            self.assertEqual(data['title'], 'Test Movie')
            self.assertEqual(data['year'], 2022)
            self.assertEqual(data['rating'], 8.0)
            self.assertEqual(data['runtime'], 120)



if __name__ == '__main__':
    unittest.main()
