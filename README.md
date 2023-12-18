# Backend Developer Challenge - Movie API

## The Challenge

IMDb provides tab-separated files with movie listings, and we challenge you to create a REST API that lists movies from these files with specific requirements. The challenge focuses on movies exclusively.

1. **API Endpoints:**
   - GET /movies
   - GET /movies/{id}
   - POST /movies

2. **Movie Details in JSON Response:**
   - Title
   - Category/Genre
   - Year
   - Rating
   - Runtime
   - IMDb Page Link

3. **Sorting:**
   - Year
   - Rating
   - Title

4. **Filtering:**
   - Category/Genre
   - Rating

You should be able to list movies and facilitate searches, such as retrieving Action movies with a rating greater than 8.5.

## Data Source

Download relevant data files from [IMDb Datasets](https://datasets.imdbws.com/). Refer to the [IMDb Interfaces](https://www.imdb.com/interfaces/) for file descriptions.

## Guidelines

- **Reorganize the data as needed.**
- **Update requirements as necessary.**
- **API Example**: [IMDb Top 1000](https://www.imdb.com/search/title/?groups=top_1000&view=simple&sort=user_rating,desc).

## Instruction Completion and Deliverables

- **Use your preferred technology, with SQL DB or MongoDB preferred.**
   For storage, it has been decided on a PostgreSQL database delivered in a Docker container. The Docker distribution is explained below in [Docker](https://github.com/Francescde/ApiMovieIMDB/tree/main?tab=readme-ov-file#docker).

- **Schema/Script for Generating Storage:**
   The data-loader documentation, available at [Data-loader Documentation](https://github.com/Francescde/ApiMovieIMDB/tree/main/solution/data-loader), provides detailed information on the schema and script for generating storage. It outlines how the dataset is organized and loaded into the PostgreSQL database.

- **API with OpenAPI Description:**
   The API documentation, accessible at [API Documentation](https://github.com/Francescde/ApiMovieIMDB/tree/main/solution/api), includes an OpenAPI description. This documentation offers insights into the API's structure, available endpoints, request-response formats, and usage guidelines.

   The API is built on Flask, a Python web framework. The decision to use Flask over Django was due to the simplicity of the app, which didn't require the prebuilt utilities Django offers.

   The OpenAPI documentation is available in the [docs subfolder](https://github.com/Francescde/ApiMovieIMDB/tree/main/solution/api/docs). The openapi.yml file defines the API's structure, including available endpoints, request parameters, and response formats.

   The OpenAPI documentation is used for the SwaggerUI [Swagger documentation](http://localhost:5000/docs/) available when the project is up and running.

- **Pagination Technique Implementation:**
   Keyset pagination has been implemented for listing movies within the API. This choice was made due to the dataset's size, where offset pagination could be inefficient. Additionally, as the dataset lacks a clear distribution of values, and some ranges could be extensive, seek pagination was deemed less suitable for this particular use case. The implementation ensures efficient handling of large datasets while providing stable and predictable performance.
   ```python
   # Apply sorting as there are fields with no unique values; add a second field to ensure being deterministic
   descendent = 'desc' in query_params
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
   if not page_size or not page_size.isdigit():
       page_size=10
   # Retrieve and paginate the results taking genres in eager mode
   movies = query.options(joinedload(Movie.genres)).limit(int(page_size)).all()  # Adjust the limit as needed
   ```

## Deadline

Please respond within one week, by the end of the day on XXXXXXXXX.

## Running the Project

1. Ensure Docker and Docker Compose are installed.
2. Clone the repository: `git clone <repository-url>`
   ```bash
   git clone https://github.com/Francescde/ApiMovieIMDB.git
   ```
3. Navigate to the project directory: `cd ApiMovieIMDB`
   ```bash
   cd ApiMovieIMDB
   ```
4. Run Docker Compose: `docker-compose up --build`
   ```bash
   docker-compose up --build
   ```

Access the application at `http://localhost:5000` and the Swagger documentation at `http://localhost:5000/docs`.

## Docker

This project uses Docker with two services, `postgres` and `solution`.

## Docker Compose

### 1. Postgres

- **Image:** postgres:latest
- **Environment Variables:**
  - POSTGRES_USER: your_user
  - POSTGRES_PASSWORD: your_password
  - POSTGRES_DB: your_database
- **Volumes:** Mounts SQL scripts from `./sql-scripts` to `/docker-entrypoint-initdb.d`
- **Ports:** Forwards host port 5432 to container port 5432

### 2. Solution

- **Build Context:** ./solution
- **Depends On:** Postgres (waits for the database service to be ready)
- **Ports:** Forwards host port 5000 to container port 5000
- **Environment Variables:**
  - DB_HOST: postgres
  - DB_PORT: 5432
  - DB_USER: your_user
  - DB_PASSWORD: your_password
  - DB_NAME: your_database

## Solution Service

### Dockerfile

1. **Builder:** Python 3.8 base image for dependencies.
2. **Downloader:** Alpine Linux for downloading dockerize.
3. **Installation and Test:** Install requirements and execute tests for expected behavior.
4. **Final Image:** Python 3.8, dockerize, and application installation.

### run.sh

Sets up environment variables, creates a JSON configuration file, and runs data-loader and the Flask API using Gunicorn.

## Data-loader

Project to load the dataset into the PostgreSQL database.

Details

: [Data-loader Documentation](https://github.com/Francescde/ApiMovieIMDB/tree/main/solution/data-loader)

## API

Flask app with RESTful API in the `api` directory. The `startup` module starts the API using Gunicorn.

Details: [API Documentation](https://github.com/Francescde/ApiMovieIMDB/tree/main/solution/api)

# Todo

1. **Optimize Storage for IMDb Link:**
   Consider storing IMDb IDs instead of full IMDb links to conserve database space. Storing IMDb links can be resource-intensive, and generating the link dynamically within the API when fetching the resource could be a more space-efficient approach. IMDb IDs can be extracted from the URL provided during the movie post request.

2. **Enhance API Integration Tests:**
   Improve API integration tests by leveraging `pytest-docker` to instantiate a Dockerized PostgreSQL database. Testing on an environment that mirrors the actual API setup provides more accurate and realistic results compared to the current in-memory SQLLittle setup.

# Curiosity

- **Use of UUIDs for Security:**
  Instead of utilizing the same IDs as those provided by the IMDb dataset, UUIDs have been adopted for security reasons. This practice enhances security by ensuring unpredictability in resource identifiers, minimizing the risk associated with exposing internal identifiers used in the IMDb dataset. The use of UUIDs adds an extra layer of confidentiality and data protection.
