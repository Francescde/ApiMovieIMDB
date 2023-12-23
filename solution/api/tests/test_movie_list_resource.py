import unittest
from flask import Flask, request
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_testing import TestCase
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from resources.movie import MovieResource
from models.main import db, Movie, Genre
from app import MovieAPI

class TestMovieListResource(TestCase):
    
    def create_app(self):
        # Use an in-memory SQLite database for testing
        movieApi = MovieAPI('sqlite:///:memory:')
        app = movieApi.app
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        return app

        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_movies_with_valid_params(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        movie1 = Movie(title='Movie 1', year=2020, rating=7.6, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(title='Movie 2', year=2021, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=rating&desc=true&genre=Action&rating_gt=7.5&after_id=' + movie2.id + '&page_size=5')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Movie 1')

    def test_get_movies_with_invalid_sort_field(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        movie = Movie(title='Movie 1', year=2020, rating=7.5, runtime=110)
        movie.genres.append(genre)
        db.session.add(movie)
        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=invalid_field')

        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertEqual(data['message'], 'Invalid sort field')


    def test_get_movies_with_valid_sort_field(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        movie1 = Movie(title='Movie 1', year=2020, rating=7.5, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(title='Movie 2', year=2021, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=year')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Movie 1')
        self.assertEqual(data[1]['title'], 'Movie 2')

    def test_get_movies_with_same_sort_field_value(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        # Creating movies with the same rating
        movie1 = Movie(id='1', title='Movie 1', year=2020, rating=8.0, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(id='2', title='Movie 2', year=2021, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=rating')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        # Since the rating is the same, the sorting should be based on the 'id'
        self.assertEqual(data[0]['title'], 'Movie 1')
        self.assertEqual(data[1]['title'], 'Movie 2')

    def test_get_movies_desc_with_same_sort_field_value(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        # Creating movies with the same rating
        movie1 = Movie(id='1', title='Movie 1', year=2020, rating=8.0, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(id='2', title='Movie 2', year=2021, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=rating&desc')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        # Since the rating is the same, the sorting should be based on the 'id'
        self.assertEqual(data[0]['title'], 'Movie 1')
        self.assertEqual(data[1]['title'], 'Movie 2')

    def test_get_movies_desc_with_same_year_value(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        # Creating movies with the same rating
        movie1 = Movie(id='2', title='Movie 1', year=2020, rating=8.0, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(id='1', title='Movie 2', year=2020, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        movie3 = Movie(id='3', title='Movie 3', year=2019, rating=8.0, runtime=110)
        movie3.genres.append(genre)
        db.session.add(movie3)

        movie4 = Movie(id='4', title='Movie 4', year=2021, rating=8.0, runtime=120)
        movie4.genres.append(genre)
        db.session.add(movie4)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=year&desc')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 4)
        # Since the rating is the same, the sorting should be based on the 'id'
        self.assertEqual(data[0]['title'], 'Movie 4')
        self.assertEqual(data[1]['title'], 'Movie 2')
        self.assertEqual(data[2]['title'], 'Movie 1')
        self.assertEqual(data[3]['title'], 'Movie 3')
        self.assertEqual(data[0]['id'], '4')
        self.assertEqual(data[1]['id'], '1')
        self.assertEqual(data[2]['id'], '2')
        self.assertEqual(data[3]['id'], '3')

    def test_get_movies_desc_with_same_year_value_next_page(self):
        # Arrange
        genre = Genre(name='Action')
        db.session.add(genre)
        db.session.commit()

        # Creating movies with the same rating
        movie1 = Movie(id='2', title='Movie 1', year=2020, rating=8.0, runtime=110)
        movie1.genres.append(genre)
        db.session.add(movie1)

        movie2 = Movie(id='1', title='Movie 2', year=2020, rating=8.0, runtime=120)
        movie2.genres.append(genre)
        db.session.add(movie2)

        movie3 = Movie(id='3', title='Movie 3', year=2019, rating=8.0, runtime=110)
        movie3.genres.append(genre)
        db.session.add(movie3)

        movie4 = Movie(id='4', title='Movie 4', year=2021, rating=8.0, runtime=120)
        movie4.genres.append(genre)
        db.session.add(movie4)

        db.session.commit()

        # Act
        client = self.app.test_client()
        response = client.get('/movies?sort=year&desc&after_id=1')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['title'], 'Movie 1')
        self.assertEqual(data[1]['title'], 'Movie 3')

if __name__ == '__main__':
    unittest.main()
