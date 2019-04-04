DROP TABLE IF EXISTS user;

CREATE TABLE song (
  songid int IDENTITY(1,1) PRIMARY KEY,
  name TEXT,
  artists TEXT,
  lyrics TEXT
);
