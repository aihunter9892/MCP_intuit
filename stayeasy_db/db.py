import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "stayeasy.db"

SEED_LISTINGS = [
    ("ST001", "Modern Downtown Apartment", "Dubai", "Downtown Dubai", 2, 4, 150, 4.8,
     "WiFi,Pool,Gym,Parking", 1),
    ("ST002", "Luxury Marina View Apartment", "Dubai", "Dubai Marina", 2, 4, 220, 4.9,
     "WiFi,Pool,Gym,Sea View,Parking", 1),
    ("ST003", "Cozy JBR Beach Apartment", "Dubai", "JBR", 1, 2, 130, 4.7,
     "WiFi,Beach Access,Pool", 1),
    ("ST004", "Palm Luxury Villa", "Dubai", "Palm Jumeirah", 4, 8, 600, 4.95,
     "WiFi,Private Pool,Beach Access,Parking,Sea View", 1),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT NOT NULL,
            bedrooms INTEGER NOT NULL,
            guests INTEGER NOT NULL,
            price_per_night REAL NOT NULL,
            rating REAL NOT NULL,
            amenities TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            listing_id TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    """)

    existing = conn.execute("SELECT COUNT(*) AS n FROM listings").fetchone()["n"]

    if existing == 0:
        conn.executemany(
            """
            INSERT INTO listings
                (id, title, city, area, bedrooms, guests, price_per_night,
                 rating, amenities, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            SEED_LISTINGS,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")
