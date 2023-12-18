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
- **Thinks left todo:**
   Given the challenge's time limitations and the emphasis on showcasing problem-solving skills within those constraints, some aspects remain incomplete intentionally. The [TODO](https://github.com/Francescde/ApiMovieIMDB/tree/main?tab=readme-ov-file#todo) section provides insights into areas that would typically be addressed with more time. It's essential to note that this challenge was undertaken during personal free time, and while every effort has been made to approach it in a professional manner, certain aspects couldn't be fully addressed to the desired level.

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

1. **Post Movie Rollback:**
   The endpoint to post a movie is committing multiple times before completing, so in case of an error, inconsistent data could be stored.
# Todo

2. **Remove Magic Values:**
   Some values are hardcoded, such as the name of the columns in the data files and the port for the API. It's a good practice to make them configurable to facilitate easy replacement without modifying the code.

   - **Data Files Column Names:**
     The column names in the data files, which are currently hardcoded, should be made configurable. This ensures flexibility and ease of adaptation to different datasets without modifying the codebase.

   - **API Port Configuration:**
     The API port, currently hardcoded as 5000, should be made configurable. This allows for easy port customization without requiring changes to the source code.

   For example, consider using environment variables or a configuration file to store and retrieve these values dynamically.


3. **Improve Logging:**
   During the development process, logging was not initially prioritized. However, incorporating a robust logging system is crucial for understanding the application's behavior and diagnosing issues effectively. Logging into different levels allows for a more granular control over the information captured, providing insights into various aspects of the application.

   **Why Logging Matters:**
   - **Debugging:** Detailed logs at the `DEBUG` level help developers trace the flow of the application, making it easier to identify and fix bugs during development.

   - **Monitoring:** Information at the `INFO` level provides a high-level overview of the application's activities, aiding in monitoring its overall health and performance.

   - **Warning and Error Handling:** The `WARNING` and `ERROR` levels are essential for capturing potential issues or unexpected behaviors, enabling proactive identification and resolution.

   **How Log Levels Work in Python:**
   Python's logging module supports different log levels, including `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Each level corresponds to a specific severity of the log message. During runtime, you can configure the logging system to capture messages at or above a certain level, allowing for dynamic adjustment of verbosity.

   Example Configuration in Python:

   ```python
   import logging

   logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG for all loggers

   # Example Usage
   logging.debug("This is a debug message")
   logging.info("This is an info message")
   logging.warning("This is a warning message")
   logging.error("This is an error message")
   logging.critical("This is a critical message")
   ```

   By setting the logging level, you control which messages are recorded. For instance, if the level is set to `WARNING`, only messages with a severity of `WARNING`, `ERROR`, and `CRITICAL` will be captured.

   Introducing proper logging levels in your application enhances its maintainability, facilitates debugging, and contributes to a more efficient development and troubleshooting process.


4. **Optimize Storage for IMDb Link:**
   Consider storing IMDb IDs instead of full IMDb links to conserve database space. Storing IMDb links can be resource-intensive, and generating the link dynamically within the API when fetching the resource could be a more space-efficient approach. IMDb IDs can be extracted from the URL provided during the movie post request.

5. **Reschedule Data Loading:**
   According to the IMDb [Description](https://developer.imdb.com/non-commercial-datasets/), data is updated every day. As the data-loader is built in a way that each execution replaces the old data with the new one, scheduling a reload could be really useful.

   For example, to schedule a task to reload your Docker container every day at 2 am, you can use cron jobs. Here's how you can modify your Docker Compose file to include a cron service that triggers the reload:

   ```yaml
   version: '3'

   services:
     postgres:
       image: postgres:latest
       environment:
         POSTGRES_USER: your_user
         POSTGRES_PASSWORD: your_password
         POSTGRES_DB: your_database
       volumes:
         - ./sql-scripts:/docker-entrypoint-initdb.d
       ports:
         - "5432:5432"

     solution:
       build:
         context: ./solution
       depends_on:
         - postgres
       ports:
         - "5000:5000"
       environment:
         DB_HOST: postgres
         DB_PORT: 5432
         DB_USER: your_user
         DB_PASSWORD: your_password
         DB_NAME: your_database
         DEVELOP_SERVER: false
         SKIP_LOAD_DATA: false

     cron:
       image: alpine
       volumes:
         - ./scripts:/scripts
       depends_on:
         - solution
       command: ["sh", "-c", "crond -f -d 8"]
   ```

   Additionally, create a `scripts` folder in your project directory, and inside it, add a script named `reload.sh` with the following content:

   ```sh
   #!/bin/sh

   # Reload the solution container
   docker-compose restart solution
   ```

   Make sure to give execute permission to the script:

   ```bash
   chmod +x scripts/reload.sh
   ```

   This script will be executed by the cron job.

   Finally, add a cron job configuration file named `crontab` in the `scripts` folder with the following content:

   ```sh
   0 2 * * * /scripts/reload.sh
   ```

   This cron job will run the `reload.sh` script every day at 2 am.

   With these changes, the `solution` container would be restarted daily at 2 am. The data-loader should also have a way to alert if an execution fails because then the data would be from the previous load thanks to the rollback policy.

6. **Enhance API Integration Tests:**
   Improve API integration tests by leveraging `pytest-docker` to instantiate a Dockerized PostgreSQL database. Testing on an environment that mirrors the actual API setup provides more accurate and realistic results compared to the current in-memory SQLLittle setup.

# Curiosity

- **Use of UUIDs for Security:**
  Instead of utilizing the same IDs as those provided by the IMDb dataset, UUIDs have been adopted for security reasons. This practice enhances security by ensuring unpredictability in resource identifiers, minimizing the risk associated with exposing internal identifiers used in the IMDb dataset. The use of UUIDs adds an extra layer of confidentiality and data protection.
