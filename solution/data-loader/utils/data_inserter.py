import math

import numpy as np
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor


class DataInserter:
    def __init__(self, db_params):
        self.engine = create_engine(
            'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params))
        self.conn = self.engine.connect()
        self.conn.autocommit = False

    def execute_insert(self, frame, table_name, enable_parallel_insert=False):
        num_rows, num_columns = frame.shape
        print(f"Inserting {num_rows} rows into {table_name}")
        if enable_parallel_insert:
            def parallel_insert(chunk):
                chunk.to_sql(name=table_name, con=self.conn, if_exists='append', index=False, method='multi', chunksize=1000)
            # Split the DataFrame into chunks
            chunks = np.array_split(frame, max(math.ceil(num_rows/100),1))

            with ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(parallel_insert, chunks)
        else:
            frame.to_sql(name=table_name, con=self.conn, if_exists='append', index=False, method='multi', chunksize=1000)


    def close_connection(self):
        self.conn.commit()
        self.conn.close()

    def truncate_table(self, table_name):
        # Truncate each table
        self.conn.execute(text(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;'))
        print(f'Table {table_name} truncated successfully.')

    def rollback(self):
        self.conn.rollback()
        self.conn.close()
