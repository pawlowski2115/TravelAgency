import sqlite3
from flask import g

DATABASE = "travel.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT NOT NULL UNIQUE,
    weather_city TEXT NOT NULL,
    currency_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    departure_date TEXT NOT NULL,
    return_date TEXT NOT NULL,
    departure_place TEXT NOT NULL,
    price_local REAL NOT NULL,
    price_pln REAL NOT NULL,
    is_sold_out INTEGER NOT NULL DEFAULT 0 CHECK (is_sold_out IN (0, 1)),
    FOREIGN KEY (destination_id) REFERENCES destinations(id) on DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS  idx_trips_destination ON trips(destination_id);
"""

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()

def init_db_command_init(app):
    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Baza danych SmartTravel została zainicjalizowana.")

def seed_db_command_init(app):
    @app.cli.command("seed-db")
    def seed_db_command():
        db = get_db()
        count = db.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
        if count == 0:
            default_destinations = [
                ["Włochy", "Rome", "EUR"],
                ["Hiszpania", "Madrid", "EUR"],
                ["Japonia", "Tokyo", "JPY"],
                ["USA", "New York", "USD"]
            ]
            db.executemany(
                "INSERT INTO destinations (country_name, weather_city, currency_code) VALUES (?, ?, ?)",
                default_destinations
            )
            db.commit()
            print("Dodano podstawowe destynacje (Włochy, Hiszpania, Japonia, USA).")
        else:
            print("Tabela destinations nie jest pusta, pomijam seedowanie.")
