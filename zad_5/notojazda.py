import sqlalchemy
import uvicorn
import io
from fastapi import FastAPI
import time
from definitions import *

engine = sqlalchemy.create_engine('postgresql://postgres:postgrespw@localhost:32778')
connection = engine.connect()

app = FastAPI()

FILE_PATH = "createdb.sql"


@app.get("/apply_schema")
def apply_schema() -> str:
    # create the database schema from definitions.py

    # check if the schema is already applied for clan table
    result = connection.execute(sqlalchemy.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clan');"))
    if result.fetchmany()[0][0]:
        return "Schema already applied"

    Base.metadata.create_all(engine)
    return "Schema applied"
    

@app.get("/tables")
def get_db_tables() -> str:
    retv = io.StringIO()
    # only show tables that are not system tables
    query = """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema='public' AND table_type='BASE TABLE';
               """
    for table in connection.execute(sqlalchemy.text(query)):
        retv.write(f"{table[0]}    ")
    return retv.getvalue().strip()


if __name__ == "__main__":
    # run the app with uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    connection.close()


