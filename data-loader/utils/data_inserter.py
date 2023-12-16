from sqlalchemy import create_engine, text


class DataInserter:
    def __init__(self, db_params):
        self.engine = create_engine(
            'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(**db_params))
        self.conn = self.engine.connect()
        self.conn.autocommit = False

    def execute_insert(self, frame, table_name):
        num_rows, num_columns = frame.shape
        print(f"Inserting {num_rows} rows into {table_name}")
        frame.to_sql(name=table_name, con=self.conn, if_exists='append', index=False, method="multi", chunksize=1000)

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
