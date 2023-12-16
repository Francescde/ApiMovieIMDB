import pandas as pd
import uuid
from sqlalchemy import create_engine, text
import requests
from io import BytesIO
import gzip



print("Script is running...")
# Function to download and extract a gzip file
def download_and_extract(url):
    response = requests.get(url)
    with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as file:
        content = file.read()
    return content

# Database connection parameters
# Update this line in load_data.py
db_params = {
    "host": "postgres",
    "port": 5432,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database",
}

def assignNonNullsTitles(dataFrame, columnName):
    akas_file_path = "title.akas.tsv"

    # Read the "title.akas.tsv" file into a DataFrame
    akas_df = pd.read_csv(akas_file_path, sep='\t')
    # Remove rows with null titles
    filtered_df = akas_df.dropna(subset=['title'])
    filtered_df['isOriginalTitle'] = pd.to_numeric(filtered_df['isOriginalTitle'], errors='coerce').fillna(0)
    sorted_df = filtered_df.sort_values(by='isOriginalTitle', ascending=False)
    # Remove duplicate appearances, keeping the first occurrence
    final_titles_df = sorted_df.drop_duplicates(subset='titleId', keep='first')[['titleId', 'title']]
    merged_df = pd.merge(dataFrame, final_titles_df, how='left', left_on='tconst', right_on='titleId')
    merged_df[columnName] = merged_df[columnName].fillna(merged_df['title'])

    return merged_df

print("Connecting to db")

# Create a connection to the PostgreSQL database
engine = create_engine('postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params))
conn = engine.connect()
#conn.execute(text("DROP TABLE IF EXISTS movies CASCADE"))
print("downloading data")

def download_df(url):
    content = download_and_extract(url)
    return pd.read_csv(BytesIO(content), sep='\t')
'''
basics_df = download_df("https://datasets.imdbws.com/title.basics.tsv.gz")

print("basics", basics_df.last_valid_index)

ratings_df = download_and_extract("https://datasets.imdbws.com/title.ratings.tsv.gz")

print("ratings", ratings_df.last_valid_index)
'''
basics_df = pd.read_csv("title.basics.tsv", sep='\t')
print("basics", basics_df.last_valid_index)
ratings_df = pd.read_csv("title.ratings.tsv", sep='\t')
print("ratings", ratings_df.last_valid_index)

# Assuming you have created the movies, genres, and movie_genres tables

# Insert data into the movies table, including ratings
filtered_basics_df = basics_df[basics_df['titleType'] == 'movie']
filtered_basics_df.loc[:, "movie_id"] = filtered_basics_df["tconst"].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_URL, x)))

filtered_basics_df = filtered_basics_df.drop_duplicates(subset='tconst')
filtered_basics_df.loc[:,"runtimeMinutesNotNull"] = filtered_basics_df["runtimeMinutes"].replace(r"\N", None)
filtered_basics_df.loc[:,"startYearNonNull"] = filtered_basics_df["startYear"].replace(r"\N", None)
filtered_basics_df = assignNonNullsTitles(filtered_basics_df, "primaryTitle")
filtered_basics_df = filtered_basics_df.dropna(subset=['primaryTitle'])


movies_data = pd.merge(filtered_basics_df, ratings_df, on="tconst", how="left")
movies_data["ratingNotNull"] = movies_data["averageRating"].replace(r"\N", None)
movies_data = movies_data[["movie_id", "primaryTitle", "startYearNonNull", "runtimeMinutesNotNull", "ratingNotNull"]]
movies_data.columns = ["id", "title", "year", "runtime", "rating"]
print("movies_data")
print(movies_data.head())
print(movies_data.iloc[922])
print(movies_data["runtime"])
print("inserting movies_data")

def execute_upsert(frame, table_name):
    print("inserting ", table_name)
    frame.to_sql(name=table_name, con=conn, if_exists='append', index=False, method="multi", chunksize=1000)
execute_upsert(movies_data, "movies")

#movies_data.to_sql("movies", con=conn, if_exists="append", index=False, method="multi", chunksize=1000, index_label="id")

# Insert data into the genres table
genres_movie_data = filtered_basics_df[["movie_id", "genres"]]

genres_movie_data["genres"] = genres_movie_data["genres"].apply(lambda x: x.split(','))
genres_movie_data = genres_movie_data.explode("genres").dropna()

# Drop rows with '\N' values in the "genres" column
genres_movie_data = genres_movie_data[genres_movie_data["genres"] != r"\N"]

genres_movie_data["genre_id"] = genres_movie_data["genres"].apply(lambda x: str(uuid.uuid5(uuid.NAMESPACE_URL, x)))
genres_data = genres_movie_data[["genre_id", "genres"]]
genres_data.columns = ["id", "name"]
genres_data = genres_data.drop_duplicates(subset='id')
print("genres_data")
print(genres_data.head())
print("inserting genres_data")

# genres_data.to_sql("genres", con=conn, if_exists="append", index=False, method="multi", chunksize=1000, index_label="id")

execute_upsert(genres_data, "genres")
# Insert data into the movie_genres table
movie_genres_data = genres_movie_data[["movie_id", "genre_id"]]
movie_genres_data.columns = ["movie_id", "genre_id"]
print(movie_genres_data.head())
#movie_genres_data.to_sql("movie_genres", con=conn, if_exists="append", index=False, method="multi", chunksize=1000)

execute_upsert(movie_genres_data, "movie_genres")

# Close the database connection
conn.close()
