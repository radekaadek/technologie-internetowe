import sqlalchemy
import uvicorn
from fastapi import FastAPI

engine = sqlalchemy.create_engine('postgresql://postgres:postgrespw@localhost:32771')
connection = engine.connect()

app = FastAPI()

FILE_PATH = "createdb.sql"

def get_schema_from_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        db_schema = f.read()
    return db_schema

def enter_schema(connection: sqlalchemy.Connection, schema: str) -> None:
    connection.execute(sqlalchemy.text(schema))

@app.get("/")
def get_db_tables():
    retv = ""
    inspector = sqlalchemy.inspect(engine)
    schemas = inspector.get_schema_names()
    for schema in schemas:
        for table_name in inspector.get_table_names(schema=schema):
            for column in inspector.get_columns(table_name, schema=schema):
                retv += f"{str(column)}\n"
    return retv

connection.close()

if __name__ == "__main__":
    # run the app with uvicorn
    uvicorn.run(app, host="localhost", port=8000)
