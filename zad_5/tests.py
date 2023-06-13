import requests


def test_server_is_running():
    # check if the server is running
    r = requests.get("http://localhost:8000")
    print(r.json())
    assert r.status_code == 200


def test_delete_all():
    r = requests.delete("http://localhost:8000/delete_all")
    assert r.status_code == 204


def test_get_player_deleted():
    # get the player that doesn't exist
    r = requests.get("http://localhost:8000/player/1")
    assert r.status_code == 404


def test_post_player():
    # create a new player
    r = requests.post("http://localhost:8000/player", params={
        "username": "test",
        "password_hash": "test",
        "email": "radae@radar.com",
    })
    assert r.status_code == 201


def test_get_player_by_username():
    # get the player we just created
    r = requests.get("http://localhost:8000/player", params={
        "username": "test"
        })
    assert r.status_code == 200
    assert r.json()["username"] == "test"
    assert r.json()["email"] == "radae@radar.com"
    if r.json()["id"] is not None:
        global player_id
        player_id = r.json()["id"]


def test_post_server():
    # create a new server
    if player_id != 0:
        r = requests.post("http://localhost:8000/server", params={
            "name": "test",
            "ip": "234.17.118.75",
            "port": 27015,
            "owner_id": player_id
        })
        assert r.status_code == 201
    else:
        assert False


def test_update_player():
    # update the player we just created
    if player_id != 0:
        r = requests.put(f"http://localhost:8000/player/{player_id}", params={
            "username": "test2",
            "password_hash": "test2",
            "email": "dsa@dsa.com"
        })
        assert r.status_code == 204
    else:
        assert False


def test_get_player_updated():
    # get the player we just updated
    if player_id != 0:
        r = requests.get(f"http://localhost:8000/player/{player_id}")
        assert r.status_code == 200
        assert r.json()["username"] == "test2"
        assert r.json()["email"] == "dsa@dsa.com"
        assert r.json()["password_hash"] == "test2"
    else:
        assert False


def test_delete_player():
    # delete the player we just created
    if player_id != 0:
        r = requests.delete(f"http://localhost:8000/player/{player_id}")
        assert r.status_code == 204
    else:
        assert False


def test():
    # get the player we just deleted
    if player_id != 0:
        r = requests.get(f"http://localhost:8000/player/{player_id}")
        assert r.status_code == 404
    else:
        assert False


def test_populate_server():
    # populate the server
    r = requests.get("http://localhost:8000/populate")
    assert r.status_code == 201
    # clean up
    r = requests.delete("http://localhost:8000/delete_all")
