import sqlite3
from db.add_death_dto import AddDeathDTO


class DB:
    def __init__(self, path="db.sqlite"):
        # FIXME probably going to need to change this `check_same_thread`
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        try:
            with self.con:
                self.con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS deaths (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stream_title TEXT,
                        timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create tables: {e}") from e

    def add_death(self, data: AddDeathDTO):
        try:
            with self.con:
                self.con.execute(
                    "INSERT INTO deaths (stream_title, timestamp) VALUES (?, ?)",
                    (data.stream_title, data.timestamp),
                )
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed add death: {e}") from e

    def count_deaths(self):
        try:
            with self.con:
                return self.con.execute("SELECT COUNT(*) FROM deaths").fetchone()[0]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed return deaths: {e}") from e

    def close(self):
        self.con.close()
