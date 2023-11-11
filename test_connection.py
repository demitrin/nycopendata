from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os

# usage
# DB_URI=postgresql://avimoondra:password@localhost:5432/postgres python3 test_connection.py

engine = create_engine(os.getenv("DB_URI"))

def app():
    with engine.connect() as conn:
        stmt = text("select * from pg_database")
        print(conn.execute(stmt).fetchall())

if __name__ == "__main__":
    app()