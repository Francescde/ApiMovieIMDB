from flask_restful import Resource
from sqlalchemy.orm import joinedload

from models.main import MovieSchema, Movie


class MovieSingleResource(Resource):
    def get(self, movie_id):
        movie_schema = MovieSchema(many=False)
        '''Get a single movie by its ID'''
        movie = Movie.query.options(joinedload(Movie.genres)).get(movie_id)

        if not movie:
            return {'message': 'Movie not found'}, 404

        # Manually construct the serialized output with genres
        serialized_movie = movie_schema.dump(movie)
        serialized_movie['genres'] = [{'name': genre.name} for genre in movie.genres]

        return serialized_movie
