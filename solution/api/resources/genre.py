from flask_restful import Resource

from models.main import GenreSchema, Genre


class GenreResource(Resource):

    def get(self):
        genres_schema = GenreSchema(many=True)
        '''List all genres'''
        genres = Genre.query.all()
        return genres_schema.dump(genres)
