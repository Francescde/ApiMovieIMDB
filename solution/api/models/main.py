import uuid

from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())

movie_genre_association = db.Table(
    'movie_genres',
    db.Column("movie_id", db.String(36), db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    db.Column("genre_id", db.String(36), db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)

class Genre(db.Model):
    __tablename__ = "genres"
    #id = db.Column(db.String(36), default=db.text("uuid_generate_v4()"), primary_key=True) #exclusive to postgress
    id = db.Column(db.String(36), default=generate_uuid, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    movies = db.relationship("Movie", secondary=movie_genre_association, back_populates='genres')

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.String(36), default=generate_uuid, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    runtime = db.Column(db.Integer)
    imdb_link = db.Column(db.String(255))
    genres = db.relationship("Genre", secondary=movie_genre_association, back_populates='movies')


class GenreSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Genre

class MovieSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Movie