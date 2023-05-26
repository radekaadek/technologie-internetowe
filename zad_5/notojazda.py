import sqlalchemy as db
import uvicorn
import io
from faker import Faker
from fastapi import FastAPI
from definitions import Base

engine: db.engine.Engine
conn: db.engine.Connection

fake = Faker()
app = FastAPI()

OUTPUT_FILE = "output.txt"


@app.get("/apply_schema")
def apply_schema() -> str:
    # create the database schema from definitions.py
    # check if the schema is already applied for clan table
    query = """"SELECT EXISTS (
                    SELECT
                    FROM information_schema.tables
                    WHERE table_name = 'clan');"""

    result = conn.execute(db.text(query))
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
    for table in conn.execute(db.text(query)):
        retv.write(f"{table[0]}    ")
    return retv.getvalue().strip()


@app.get("/populate")
def populate_db() -> str:
    # use faker to populate the database
    for _ in range(10):
        conn.execute(db.text(f"""
            INSERT INTO clan (name, tag, created_at)
            VALUES ('{fake.name()}', '{fake.name()}',
            '{fake.date_time_this_year()}');"""))
        # set foreign key to null for now
        conn.execute(db.text(f"""
            INSERT INTO player (username, password_hash, email,
            is_admin, active, created_at, last_login, clan_id,
            server_id) VALUES ('{fake.name()}', '{fake.name()}',
            '{fake.email()}', '{fake.boolean()}', '{fake.boolean()}',
            '{fake.date_time_this_year()}', '{fake.date_time_this_year()}',
            NULL, NULL);"""))
        conn.execute(db.text(f"""
            INSERT INTO server (name, ip, port, created_at, owner_id)
            VALUES ('{fake.name()}', '{fake.ipv4()}', '{fake.port_number()}',
            '{fake.date_time_this_year()}', NULL);"""))
        conn.execute(db.text(f"""
            INSERT INTO achievement (name, description)
            VALUES ('{fake.name()}', '{fake.text()}');"""))
    return "Populated"


@app.get("/show_tables_content")
def show_tables_content() -> str:
    retv = ""
    # show all tables and their content
    for table in Base.metadata.tables:
        retv += f"{table}\n"
        for row in conn.execute(db.text(f"""SELECT *
                                                      FROM {table}""")):
            retv += f"{row}\n"
    with open(OUTPUT_FILE, "w") as f:
        f.write(retv)
    return retv


@app.get("/get_players")
def get_players() -> list:
    # get all players
    players = []
    for player in conn.execute(db.text("SELECT * FROM player")):
        players.append(player)
    return players


if __name__ == "__main__":
    connstr = "postgresql://postgres:postgrespw@localhost:32779"
    engine = db.create_engine(connstr)
    conn = engine.connect()
    # run the app with uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    conn.close()
