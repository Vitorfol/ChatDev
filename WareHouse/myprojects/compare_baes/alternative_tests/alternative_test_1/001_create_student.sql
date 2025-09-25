'''
Initial migration: create student table with id and name.
'''
-- Initial migration: create student table with id and name.
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);