DROP TABLE IF EXISTS song;
DROP TABLE IF EXISTS artists;

CREATE TABLE song (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  lyrics TEXT
);

CREATE TABLE artists (
    artist TEXT,
    songname INTEGER
);
