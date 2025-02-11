CREATE TABLE IF NOT EXISTS virtual_machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    ram INT,
    cpu INT,
    password_hash VARCHAR
);

CREATE TABLE IF NOT EXISTS disks (
    id SERIAL PRIMARY KEY,
    vm_id INT REFERENCES virtual_machines(id) ON DELETE CASCADE,
    size INT NOT NULL
);
