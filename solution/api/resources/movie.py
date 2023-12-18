import sqlalchemy
from flask import request
from flask_restful import Resource
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models.main import MovieSchema, Movie, Genre, db


class MovieResource(Resource):

    def get(self):
        movies_schema = MovieSchema(many=True)
        '''List all movies with sorting, filtering, and keyset pagination'''
        query_params = request.args.to_dict()

        # Extract and validate sorting parameters
        valid_sort_fields = ['title', 'year', 'rating']
        sort_field = query_params.get('sort', 'title')
        if sort_field not in valid_sort_fields:
            return {'message': 'Invalid sort field'}, 400

        # Extract and validate filtering parameters
        filter_params = {}
        valid_filter_fields = ['genre', 'rating_gt']
        for key, value in query_params.items():
            if key in valid_filter_fields:
                filter_params[key] = value

        # Extract and validate keyset pagination parameters
        valid_pagination_fields = ['id', 'title', 'year', 'rating']
        after_id = query_params.get('after_id')
        if after_id and sort_field not in valid_pagination_fields:
            return {'message': 'Invalid pagination field for keyset pagination'}, 400

        # Build the query based on sorting and filtering parameters
        query = Movie.query

        for key, value in filter_params.items():
            if key == 'genre':
                query = query.join(Movie.genres).filter(Genre.name == value)
            elif key == 'rating_gt':
                query = query.filter(Movie.rating > float(value))

        # Apply sorting as there are fields with no unique values add a second field to ensure being deterministic
        # Implement keyset pagination
        # Use a subquery to get the value of the sorting field for the specified after_id
        descendent = query_params.get('desc')
        if not descendent or not int(descendent) == 1:
            if after_id:
                subquery = Movie.query.filter(Movie.id == after_id).subquery()
                query = query.filter(sqlalchemy.or_(
                    getattr(Movie, sort_field) > subquery.c[sort_field],
                    sqlalchemy.and_(
                        getattr(Movie, sort_field) == subquery.c[sort_field],
                        Movie.id < subquery.c.id
                    )
                )).params(after_id=after_id)
            query = query.order_by(getattr(Movie, sort_field), Movie.id)
        else:
            if after_id:
                subquery = Movie.query.filter(Movie.id == after_id).subquery()
                query = query.filter(sqlalchemy.or_(
                    getattr(Movie, sort_field) < subquery.c[sort_field],
                    sqlalchemy.and_(
                        getattr(Movie, sort_field) == subquery.c[sort_field],
                        Movie.id < subquery.c.id
                    )
                )).params(after_id=after_id)
            query = query.order_by(desc(getattr(Movie, sort_field)), Movie.id)
        page_size = query_params.get('page_size')
        if not page_size or not page_size.isdigit():
            page_size=10
        # Retrieve and paginate the results taking genres in eager mode
        movies = query.options(joinedload(Movie.genres)).limit(int(page_size)).all()  # Adjust the limit as needed

        serialized_movies = movies_schema.dump(movies)
        # genres aren't serializing as they should. this is a workaround
        for serialized_movie, movie in zip(serialized_movies, movies):
            serialized_movie['genres'] = [{'name': genre.name} for genre in movie.genres]

        return serialized_movies

    def post(self):
        movies_schema = MovieSchema(many=False)
        '''Create a new movie'''
        data = request.json

        # Extract genres from the request data
        genres_data = data.pop('genres', [])
        print(data)

        # Create a new movie without genres
        new_movie = Movie(**data)

        db.session.add(new_movie)
        # Serialize the movie with genres
        db.session.commit()

        # Add genres to the new movie
        for genre_data in genres_data:
            print(genre_data['name'])
            genre = Genre.query.filter_by(name=genre_data['name']).first()
            if not genre:
                genre = Genre(name=genre_data['name'])
                db.session.add(genre)
                db.session.commit()
            new_movie.genres.append(genre)
            db.session.commit()
        serialized_movie = movies_schema.dump(new_movie)
        serialized_movie['genres'] = genres_data

        return serialized_movie, 201
