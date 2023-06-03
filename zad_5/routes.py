import sqlalchemy as db
import uvicorn
import datetime
from faker import Faker
from fastapi import FastAPI, HTTPException
from table_definitions import Base
from sqlalchemy import insert, select, update, delete

engine: db.engine.Engine
conn: db.engine.Connection

fake = Faker()
app = FastAPI()

OUTPUT_FILE = "output.txt"


@app.get("/", status_code=200)
def root() -> str:
    return "Hello world!"


@app.post("/apply_schema", status_code=201)
def apply_schema() -> str:
    Base.metadata.create_all(engine)
    return "Schema applied"


@app.get("/tables", status_code=200)
def get_db_tables() -> list:
    tables = []
    # only show tables that are not system tables
    query = """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema='public' AND table_type='BASE TABLE';
               """
    for table in conn.execute(db.text(query)):
        tables.append(table[0])
    return tables


@app.get("/populate", status_code=201)
def populate_db() -> None:
    clan_table = db.Table("clan", Base.metadata, autoload=True)
    player_table = db.Table("player", Base.metadata, autoload=True)
    server_table = db.Table("server", Base.metadata, autoload=True)
    achieve_table = db.Table("achievement", Base.metadata, autoload=True)
    # use faker to populate the database
    for _ in range(10):
        # insert using sqlalchemy
        clan = {"name": fake.name(), "tag": fake.name(),
                "created_at": fake.date_time_this_year()}
        ins = insert(clan_table).values(clan)
        conn.execute(ins)

        player = {"username": fake.name(), "password_hash": fake.name(),
                  "email": fake.email(), "is_admin": fake.boolean(),
                  "active": fake.boolean(),
                  "created_at": fake.date_time_this_year(),
                  "last_login": fake.date_time_this_year(),
                  "clan_id": None, "server_id": None}
        ins = insert(player_table).values(player)
        conn.execute(ins)

        server = {"name": fake.name(), "ip": fake.ipv4(),
                  "port": fake.port_number(),
                  "created_at": fake.date_time_this_year(),
                  "owner_id": None}
        ins = insert(server_table).values(server)
        conn.execute(ins)

        achievement = {"name": fake.name(), "description": fake.text()}
        ins = insert(achieve_table).values(achievement)
        conn.execute(ins)

    return


@app.post("/player", status_code=201)
def add_player(username: str, password_hash: str, email: str,
               is_admin: bool, server_id: int, clan_id: str = None) -> None:
    # add a player
    if not username or not password_hash or not\
            email or not is_admin or not server_id:
        raise HTTPException(status_code=400, detail="Bad request")
    player = {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "is_admin": is_admin,
        "active": True,
        "created_at": datetime.datetime.now(),
        "last_login": datetime.datetime.now(),
        "clan_id": clan_id,
        "server_id": server_id
    }
    player_table = db.Table("player", Base.metadata)
    conn.execute(insert(player_table, player))
    return


@app.get("/player/{player_id}", status_code=200)
def get_player(player_id: int) -> dict:
    # print out request parameters
    print(f"{player_id=}")
    # get player by id
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        player_table.c.id == player_id)).fetchone()
    # handle any errors
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.put("/player/{player_id}", status_code=204)
def update_player(player_id: int, username: str = None,
                  password_hash: str = None, email: str = None,
                  is_admin: bool = None, active: bool = None,
                  created_at: datetime.datetime = None,
                  last_login: datetime.datetime = None,
                  clan_id: int = None, server_id: int = None) -> None:
    # update player by id
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        db.Table("player").c.id == player_id)).fetchone()
    # handle any errors
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    # only update the fields that are not None
    for param in [username, password_hash, email, is_admin, active,
                  created_at, last_login, clan_id, server_id]:
        if param is not None:
            player[param] = param
    conn.execute(update(player_table).where(
        db.Table("player").c.id == player_id).values(player))
    return


@app.delete("/player/{player_id}", status_code=204)
def delete_player(player_id: int) -> None:
    # delete player by id
    table = db.Table("player", Base.metadata)
    player = conn.execute(select(db.Table("player")).where(
        table.c.id == player_id)).fetchone()
    # handle any errors
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    conn.execute(delete(table).where(
        table.c.id == player_id))
    return


@app.get("/players")
def players() -> list[dict]:
    # get all players
    players: list[dict] = []
    player_table = db.Table("player", Base.metadata)
    players = conn.execute(select(player_table)).fetchall()
    return list(players)


if __name__ == "__main__":
    connstr = "postgresql://postgres:postgrespw@localhost:32768"
    engine = db.create_engine(connstr)
    conn = engine.connect()
    # run the app with uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    conn.close()
