-- Minecraft Farming Database time is a UNIX timestamp in milliseconds

CREATE TABLE position (
    id SERIAL PRIMARY KEY,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    z INTEGER NOT NULL,
    dimension VARCHAR(255) NOT NULL,
    CHECK (dimension IN ('overworld', 'nether', 'end'))
);

CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    image_url VARCHAR(255) NOT NULL,
    max_stack INTEGER NOT NULL
);

CREATE TABLE player (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    position_id INTEGER NOT NULL REFERENCES position(id),
    hp INTEGER NOT NULL,
    hunger INTEGER NOT NULL,
    skin_url VARCHAR(255) NOT NULL,
    last_login INTEGER NOT NULL,
    cape_url VARCHAR(255) NOT NULL
);

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES player(id),
    content VARCHAR(1000) NOT NULL,
    unix_time INTEGER NOT NULL,
    is_private BOOLEAN NOT NULL,
    recipient_id INTEGER REFERENCES player(id)
);

CREATE TABLE farm (
    id SERIAL PRIMARY KEY,
    farm_name VARCHAR(255) NOT NULL UNIQUE,
    position_id INTEGER NOT NULL REFERENCES position(id),
    last_visited INTEGER NOT NULL,
    last_visited_by INTEGER NOT NULL REFERENCES player(id),
    created_at INTEGER NOT NULL,
    max_storage INTEGER NOT NULL
);

CREATE TABLE farm_production (
    farm_id INTEGER NOT NULL REFERENCES farm(id),
    item_id INTEGER NOT NULL REFERENCES item(id),
    amount INTEGER NOT NULL,
    PRIMARY KEY (farm_id, item_id)
);

CREATE TABLE storage (
    id SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL REFERENCES position(id),
    max_storage INTEGER NOT NULL,
    name VARCHAR(255) UNIQUE
);

CREATE TABLE storage_items (
    id INTEGER NOT NULL REFERENCES storage(id),
    item_id INTEGER NOT NULL REFERENCES item(id),
    amount INTEGER NOT NULL
);

CREATE TABLE player_inventory (
    player_id INTEGER NOT NULL REFERENCES player(id),
    item_id INTEGER NOT NULL REFERENCES item(id),
    amount INTEGER NOT NULL,
    skin_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (player_id, item_id)
);

CREATE TABLE farm_item_drop (
    farm_id INTEGER NOT NULL REFERENCES farm(id),
    item_id INTEGER NOT NULL REFERENCES item(id),
    amount INTEGER NOT NULL,
    PRIMARY KEY (farm_id, item_id)
);

CREATE TABLE entity_info (
    id VARCHAR(255) PRIMARY KEY,
    entity_name VARCHAR(255) NOT NULL UNIQUE,
    entity_description TEXT,
    image_url VARCHAR(255) NOT NULL,
    spawn_hp INTEGER NOT NULL,
    damage INTEGER,
    model_url VARCHAR(255) NOT NULL,
    hostility VARCHAR(255) NOT NULL,
    CHECK (hostility IN ('hostile', 'neutral', 'friendly'))
);

CREATE TABLE entity (
    id SERIAL PRIMARY KEY,
    postition_id INTEGER NOT NULL REFERENCES position(id),
    entity_id VARCHAR(255) NOT NULL REFERENCES entity_info(id)
);
