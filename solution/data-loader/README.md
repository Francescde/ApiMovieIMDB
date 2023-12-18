# Data Loader for Movie API

This component is responsible for loading the movie dataset into the PostgreSQL database used by the Movie API.

## Prerequisites

Before running the data loader, ensure that you have the following:

- **Python:** The data loader is written in Python, so you need to have Python installed on your system.
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
- **Dependencies:** Install the required Python dependencies by running:
  ```bash
  pip install -r requirements.txt
  ```
- **PostgreSQL Database:** Ensure that the PostgreSQL database is set up and configured with the appropriate credentials.

## Configuration

Configure the data loader by updating the `config.json` file with the necessary database connection details:

```json
{
  "DB_HOST": "your_postgres_host",
  "DB_PORT": "your_postgres_port",
  "DB_USER": "your_postgres_user",
  "DB_PASSWORD": "your_postgres_password",
  "DB_NAME": "your_postgres_database"
}
```

## Usage

To run the data loader, execute the following command:

```bash
python data_loader.py
```

This script will read the movie dataset and populate the PostgreSQL database with the relevant information.

## Running Battery Tests

To ensure the robustness and reliability of the data loader, you can run battery tests. Execute the following command:

```bash
python -m unittest discover tests
```

This will run a suite of tests to validate the functionality of the data loader.


### `data_loader.py`

This module defines the `DataLoader` class, responsible for orchestrating the extraction, transformation, and loading (ETL) process of movie data into a PostgreSQL database.

#### Class Methods:

1. **`etl_movies_genres`**: Performs the ETL process for movie genres, including truncating relevant tables, inserting movies and genres data, and populating the `movie_genres` table.

2. **`insert_movies_and_genres_rows_and_retrieve_relation`**: Inserts movie and genre data into the respective tables and returns the relationship data.

3. **`insert_movies_data_and_get_movie_genres_data`**: Inserts movie data into the `movies` table and retrieves data required for the `movie_genres` table.

4. **`truncate_tables`**: Truncates specified tables to ensure a clean slate for data loading.

#### Usage Example:

The `__main__` block demonstrates how to instantiate the `DataLoader` class, read configuration data from `config.json`, and perform the ETL process.

### `utils.data_inserter.py`

This module defines the `DataInserter` class, responsible for handling interactions with the PostgreSQL database.

#### Class Methods:

1. **`__init__`**: Initializes the class by creating a connection to the PostgreSQL database using provided parameters. Note that the commits aren't changed until the end of the transaction to ensure the rollback

2. **`execute_insert`**: Executes a bulk insert operation for a given DataFrame into a specified table.

3. **`close_connection`**: Commits changes to the database and closes the database connection.

4. **`truncate_table`**: Truncates a specified table, restarting the identity column and cascading the truncation.

5. **`rollback`**: Rolls back any uncommitted changes and closes the database connection.

### `utils.data_source.py`

This module defines the `DataSource` class, responsible for handling data sources, particularly downloading and extracting data.

#### Class Methods:

1. **`__init__`**: Initializes the class with the source URL and a flag indicating if the data is downloadable.

2. **`download_and_extract`**: Downloads and extracts data from the specified source.

3. **`download_df`**: Downloads and returns data as a Pandas DataFrame.

4. **`read`**: Reads data either from the source directly or by downloading it, based on the `downloadable` flag.

### `utils.data_transformer.py`

This module defines the `DataTransformer` class, responsible for transforming raw movie data into a format suitable for database insertion.

#### Class Methods:

1. **`get_movies_data`**: Extracts and transforms movie data, including merging basics and ratings data, handling numeric conversions, and renaming columns.

2. **`get_genres_data`**: Extracts and transforms genre data, including handling genres in the `genres_movie_data` DataFrame.

3. **`get_movie_genres_data`**: Extracts and returns data for the `movie_genres` table.

4. **`get_basics_data`**: Extracts and transforms basics data, including assigning IMDb links, generating unique IDs, handling null values, and optionally filling missing titles from the `akas_data_source`.

5. **`assign_non_nulls_titles`**: Fills null titles in the DataFrame by querying the `akas_data_source`.

These classes work together to provide a modular and organized approach to the ETL process for movie data in the IMDb dataset. The `DataLoader` orchestrates the process, utilizing the `DataInserter` for database interactions, the `DataSource` for handling data sources, and the `DataTransformer` for transforming raw data.