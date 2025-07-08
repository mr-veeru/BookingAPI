"""
Database utilities for the Fitness Studio Booking API.
Handles SQLite in-memory connection, schema creation, and seed data.
"""
import sqlite3
from datetime import datetime, timedelta
import pytz

def get_db_connection():
    """
    Establishes an in-memory SQLite connection.
    Sets row_factory to sqlite3.Row for easier access to column names.
    """
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    """
    Initializes the database schema and seeds data.
    Creates 'classes' and 'bookings' tables if they don't exist.
    Clears existing data before seeding.
    Seeds data (all times in IST) for demonstration.
    """
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            datetime TEXT NOT NULL,
            instructor TEXT NOT NULL,
            available_slots INTEGER NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            client_email TEXT NOT NULL,
            booked_at TEXT NOT NULL,
            FOREIGN KEY(class_id) REFERENCES classes(id)
        )
    ''')
    # Clear tables before seeding
    cur.execute('DELETE FROM classes')
    cur.execute('DELETE FROM bookings')
    # Seed data (all times in IST)
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    classes = [
        ("Yoga", (now + timedelta(days=1, hours=7)).strftime('%Y-%m-%d %H:%M:%S'), "Alice", 10),
        ("Zumba", (now + timedelta(days=2, hours=9)).strftime('%Y-%m-%d %H:%M:%S'), "Bob", 15),
        ("HIIT", (now + timedelta(days=3, hours=18)).strftime('%Y-%m-%d %H:%M:%S'), "Charlie", 8),
    ]
    cur.executemany('INSERT INTO classes (name, datetime, instructor, available_slots) VALUES (?, ?, ?, ?)', classes)
    conn.commit() 