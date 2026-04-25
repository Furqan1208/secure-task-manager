-- Drop existing tables to allow clean schema recreation during development
-- WARNING: This will delete all data. For existing DBs, delete database.db and restart the app.
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Users table: stores registered accounts
-- Note: Passwords are stored in plaintext for this demo version
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Tasks table: stores user-created tasks
-- Added status field (pending/completed) for task tracking
-- Added created_at timestamp for record keeping
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

