CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS movies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    year INTEGER,
    rating DECIMAL(3,1),
    runtime INTEGER,
    imdb_id VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS genres (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE,
    genre_id UUID REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

 CREATE INDEX idx_movies_id ON movies (id);
 CREATE INDEX idx_movies_title ON movies (title);
-- CREATE INDEX idx_movies_id_hash ON movies USING hash (id);
--- CREATE INDEX idx_movie_genres_genre_id ON movie_genres (genre_id);
CREATE INDEX idx_movie_genres_movie_genre_id ON movie_genres (movie_id, genre_id);
CREATE INDEX idx_genres_id ON genres (id);
-- CREATE INDEX idx_genres_id_hash ON genres USING hash (id);
--- CREATE INDEX idx_movie_genres_movie_id_hash ON movie_genres USING hash (column_name);;
