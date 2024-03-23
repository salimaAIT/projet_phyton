CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);


INSERT INTO users (id, username, password)
VALUES  (1, 'salima', '1234');
       


CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score INTEGER,
    FOREIGN KEY(username) REFERENCES users(id)
);
