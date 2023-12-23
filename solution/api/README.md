# Movie API


## OpenAPI Documentation

The OpenAPI documentation is available in the [docs](./docs) folder. The [openapi.yml](./docs/openapi.yml) file defines the API's structure, including available endpoints, request parameters, and response formats.

The OpenAPI documentation is ussed for the SwaggerUI [Swagger documentation](http://localhost:5000/docs/)

## Endpoints

### 1. **GET /movies**

Get a list of movies with options for sorting, filtering, and pagination.

#### Parameters:

- **sort**: Field to sort the movies by (title, year, rating). Default is title.
- **desc**: If desc=1, the sorting order will be in descending order.
- **genre**: Filter movies by category/genre.
- **rating_gt**: Filter movies with a rating greater than the specified value.
- **after_id**: Get movies after the specified movie ID (for keyset pagination).
- **page_size**: Size of the page. Default is 10.

#### Responses:

- **200 OK**: A list of movies. Check the response schema for details.
- **400 Bad Request**: Invalid request parameters. The response includes a message describing the issue.

#### Example Request:

```http
GET /movies?sort=rating&desc=1&genre=action&rating_gt=8.0&page_size=20
```

#### Code:

```python
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
        if 'desc' not in query_params.keys():
            if after_id:
                subquery = Movie.query.filter(Movie.id == after_id).subquery()
                query = query.filter(sqlalchemy.or_(
                    getattr(Movie, sort_field) > subquery.c[sort_field],
                    sqlalchemy.and_(
                        getattr(Movie, sort_field) == subquery.c[sort_field],
                        Movie.id > subquery.c.id
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
                        Movie.id > subquery.c.id
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
            custom_serialize(movie, serialized_movie)
        return serialized_movies
```


### 2. **POST /movies**

Create a new movie.

#### Request Body:

Provide the movie details in the request body. Use the [MovieInsert](./docs/openapi.yml#components/schemas/MovieInsert) schema.

#### Responses:

- **201 Created**: The movie has been successfully created.

#### Example Request:

```http
POST /movies
Content-Type: application/json

{
  "title": "Inception",
  "genres": ["Action", "Sci-Fi"],
  "year": 2010,
  "rating": 8.8,
  "runtime": 148,
  "imdb_link": "https://www.imdb.com/title/tt1375666/"
}
```
#### Code:

```python
    
    def post(self):
        movies_schema = MovieSchema(many=False)
        '''Create a new movie'''
        data = request.json

        # Extract genres from the request data
        genres_data = data.pop('genres', [])
        if 'imdb_link' in data.keys():
            # Assuming the URL is in the format "https://www.imdb.com/title/<imdb_id>/"
            imdb_url = data['imdb_link']

            # Extract IMDb ID using regular expression
            match = re.search(r'https://www.imdb.com/title/(\w+)(?:/)?', imdb_url)
            if match:
                imdb_id = match.group(1)
                data['imdb_id'] = imdb_id
                data.pop('imdb_link')
            else:
                # Handle the case where the URL doesn't match the expected format
                # You can raise an exception, log an error, or handle it as needed
                return {'message': 'Invalid IMDb URL format'}, 400

        # Create a new movie without genres
        new_movie = Movie(**data)

        db.session.add(new_movie)

        # Add genres to the new movie
        for genre_data in genres_data:
            print(genre_data['name'])
            genre = Genre.query.filter_by(name=genre_data['name']).first()
            if not genre:
                genre = Genre(name=genre_data['name'])
                db.session.add(genre)
            new_movie.genres.append(genre)
        db.session.commit()
        serialized_movie = movies_schema.dump(new_movie)
        custom_serialize(new_movie, serialized_movie)

        return serialized_movie, 201


```
### 3. **GET /movies/{id}**

Get details of a specific movie by ID.


#### Parameters:

- **id**: The ID of the movie.

#### Responses:

- **200 OK**: The specified movie. Check the response schema for details.
- **404 Not Found**: Movie not found.

#### Example Request:

```http
GET /movies/123456789
```
#### Code:
```python
    def get(self, movie_id):
        movie_schema = MovieSchema(many=False)
        '''Get a single movie by its ID'''
        movie = Movie.query.options(joinedload(Movie.genres)).get(movie_id)

        if not movie:
            return {'message': 'Movie not found'}, 404

        # Manually construct the serialized output with genres
        serialized_movie = movie_schema.dump(movie)
        custom_serialize(movie, serialized_movie)

        return serialized_movie
```

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Python:** The Movie API is built using Python, so you'll need to have Python installed. You can download it from the [official Python website](https://www.python.org/downloads/).

- **Virtual Environment (Optional but recommended):** It's good practice to use a virtual environment to manage dependencies for your projects. You can create a virtual environment using the following commands:

   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
- **PostgreSQL Database:** Ensure that the PostgreSQL database is set up and configured with the appropriate credentials.

## Installation

Once you have the prerequisites in place, follow these steps to install the required dependencies:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Francescde/ApiMovieIMDB.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd ApiMovieIMDB/solution/api
   ```

3. **Install Requirements:**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Movie API

With the dependencies installed, you're ready to run the Movie API. Follow these steps:

1. **Navigate to the Project Directory (if not already there):**

   ```bash
   cd ApiMovieIMDB/solution/api
   ```

2. **Run the Application:**

   ```bash
   python app.py
   ```

   This command will start the API server, and you should see output indicating that the server is running.

3. **Explore the API:**

   Open your web browser or a tool like [curl](https://curl.se/) or [Postman](https://www.postman.com/) and explore the API at [http://localhost:5000](http://localhost:5000).

   - Use the [OpenAPI documentation](./docs/openapi.yml) for details on available endpoints and request/response formats.
   - Use the [Swagger documentation](http://localhost:5000/docs/) for details on available endpoints , request/response formats and to test the api.

## Running Battery Tests

Ensure the reliability and robustness of the API by running the battery tests. Execute the following command:

```bash
python -m unittest discover tests
```

This command runs a suite of tests to validate the functionality of the Movie API.

Feel free to explore the API, test various endpoints, and integrate it into your applications. If you have any questions or encounter issues, please refer to the OpenAPI documentation or reach out to the maintainers.