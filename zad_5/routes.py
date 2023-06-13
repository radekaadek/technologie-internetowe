import re
import sqlalchemy as db
import uvicorn
import datetime
from faker import Faker
from fastapi import FastAPI, HTTPException
from sqlalchemy import insert, select, update, delete
from typing import Any, Optional

engine: db.engine.Engine
conn: db.engine.Connection

fake = Faker()
app = FastAPI()

OUTPUT_FILE = "output.txt"


@app.get("/", status_code=200)
def root() -> str:
    return "Hello world!"


@app.get("/apply_schema", status_code=201)
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

    clans = []
    players = []
    servers = []
    achievements = []
    # use faker to populate the database
    for _ in range(10):
        # insert using sqlalchemy
        clan = {"name": fake.name(), "tag": fake.name(),
                "created_at": fake.date_time_this_year()}
        clans.append(clan)

        player = {"username": fake.name(), "password_hash": fake.name(),
                  "email": fake.email(), "is_admin": fake.boolean(),
                  "active": fake.boolean(),
                  "created_at": fake.date_time_this_year(),
                  "last_login": fake.date_time_this_year(),
                  "clan_id": None, "server_id": None}
        players.append(player)

        server = {"name": fake.name(), "ip": fake.ipv4(),
                  "port": fake.port_number(),
                  "created_at": fake.date_time_this_year(),
                  "owner_id": None}
        servers.append(server)

        achievement = {"name": fake.name(), "description": fake.text()}
        achievements.append(achievement)

    conn.execute(insert(clan_table), clans)
    conn.execute(insert(player_table), players)
    conn.execute(insert(server_table), servers)
    conn.execute(insert(achieve_table), achievements)
    return


@app.post("/player", status_code=201)
def add_player(username: str, password_hash: str,
               email: str, server_id: Optional[int] = None,
               clan_id: Optional[str] = "",
               is_admin: Optional[bool] = False) -> None:
    if not username or not password_hash or not\
            email:
        raise HTTPException(status_code=400, detail="Bad request")

    # check if player already exists
    player_table = db.Table("player", Base.metadata)
    player_get = conn.execute(select(player_table).where(
        player_table.c.username == username)).fetchone()
    if player_get:
        raise HTTPException(status_code=400, detail="Player already exists")

    # check if server exists
    if server_id:
        server_table = db.Table("server", Base.metadata)
        server_get = conn.execute(select(server_table).where(
            server_table.c.id == server_id)).fetchone()
        if not server_get:
            raise HTTPException(status_code=400, detail="Server not found")

    # check if clan exists
    if clan_id:
        clan_table = db.Table("clan", Base.metadata)
        clan_get = conn.execute(select(clan_table).where(
            clan_table.c.id == clan_id)).fetchone()
        if not clan_get:
            raise HTTPException(status_code=400, detail="Clan not found")

    player = {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "is_admin": is_admin,
        "active": True,
        "created_at": datetime.datetime.now(),
        "last_login": datetime.datetime.now(),
        "server_id": server_id
    }
    if clan_id:
        player["clan_id"] = clan_id

    player_table = db.Table("player", Base.metadata)
    conn.execute(insert(player_table).values(player))
    return


@app.get("/player/{player_id}", status_code=200)
def get_player(player_id: int) -> dict[str, Any]:
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        player_table.c.id == player_id)).fetchone()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return {k: v for k, v in zip(player_table.columns.keys(), player)}


@app.put("/player/{player_id}", status_code=204)
def update_player(player_id: int, username: Optional[str] = "",
                  password_hash: Optional[str] = "", email: Optional[str] = "",
                  is_admin: Optional[bool] = False,
                  active: Optional[bool] = True,
                  clan_id: Optional[int] = None,
                  server_id: Optional[int] = None) -> None:
    # update player by id
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        player_table.c.id == player_id)).fetchone()
    # handle any errors
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    # update player
    player_dict = {k: v for k, v in zip(player_table.columns.keys(), player)}
    # update only the fields that are not None
    if username:
        player_dict["username"] = username
    if password_hash:
        player_dict["password_hash"] = password_hash
    # check validity of email with regex
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise HTTPException(status_code=400, detail="Invalid email")
        player_dict["email"] = email
    player_dict["is_admin"] = is_admin
    player_dict["active"] = active
    if clan_id:
        player_dict["clan_id"] = clan_id
    if server_id:
        player_dict["server_id"] = server_id
    conn.execute(update(player_table).where(
        player_table.c.id == player_id).values(player_dict))
    return


@app.delete("/player/{player_id}", status_code=204)
def delete_player(player_id: int) -> None:
    # delete player by id
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        player_table.c.id == player_id)).fetchone()
    # handle any errors
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    # delete cascade player
    # delete all servers owned by player
    server_table = db.Table("server", Base.metadata)
    conn.execute(delete(server_table).where(
        server_table.c.owner_id == player_id))
    # delete player
    conn.execute(delete(player_table).where(
        player_table.c.id == player_id))

    return


@app.get("/players", status_code=200)
def players() -> list[dict[str, Any]]:
    # get all players
    player_table = db.Table("player", Base.metadata)
    players = conn.execute(select(player_table)).fetchall()
    # convert to dict
    retv = []
    for player in players:
        data = {k: v for k, v in zip(player_table.columns.keys(), player)}
        retv.append(data)
    return retv


@app.get("/player", status_code=200)
def player(username: Optional[str] = "",
           email: Optional[str] = "") -> dict[str, Any]:
    # get player by username or email
    player_table = db.Table("player", Base.metadata)
    if username:
        player = conn.execute(select(player_table).where(
            player_table.c.username == username)).fetchone()
    elif email:
        player = conn.execute(select(player_table).where(
            player_table.c.email == email)).fetchone()
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return {k: v for k, v in zip(player_table.columns.keys(), player)}


@app.get("/servers", status_code=200)
def servers() -> list[dict[str, Any]]:
    # get all servers
    server_table = db.Table("server", Base.metadata)
    servers = conn.execute(select(server_table)).fetchall()
    retv = []
    for server in servers:
        data = {k: v for k, v in zip(server_table.columns.keys(), server)}
        retv.append(data)
    return retv


@app.delete("/delete_all", status_code=204)
def delete_all() -> None:
    # delete all records
    player_table = db.Table("player", Base.metadata)
    server_table = db.Table("server", Base.metadata)
    clan_table = db.Table("clan", Base.metadata)
    achievement_table = db.Table("achievement", Base.metadata)
    conn.execute(delete(player_table))
    conn.execute(delete(server_table))
    conn.execute(delete(clan_table))
    conn.execute(delete(achievement_table))
    return


@app.post("/server", status_code=201)
def create_server(name: str, ip: str, port: int, owner_id: int) -> None:
    # create a server
    # check if owner exists
    player_table = db.Table("player", Base.metadata)
    player = conn.execute(select(player_table).where(
        player_table.c.id == owner_id)).fetchone()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    server_table = db.Table("server", Base.metadata)
    server = {
        "name": name,
        "ip": ip,
        "port": port,
        "created_at": datetime.datetime.now(),
        "owner_id": owner_id
    }
    conn.execute(insert(server_table).values(server))
    return


if __name__ == "__main__":
    from table_definitions import Base
    end = "@containers-us-west-202.railway.app:5690/railway"
    conn_url = "postgresql://postgres:8L7WKCN9HFe4Pmn5n7rN" + end

    engine = db.create_engine(conn_url)
    conn = engine.connect()
    Base.metadata.create_all(engine)

    # create a connection
    uvicorn.run(app, host="localhost", port=8000)
    conn.close()
