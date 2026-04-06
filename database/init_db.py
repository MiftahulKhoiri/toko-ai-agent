"""database/init_db.py - Membuat database dan tabel"""

from database.db import engine
from database.models import Base


def init_database():
    """Membuat semua tabel di database"""
    print("Membuat database...")
    Base.metadata.create_all(bind=engine)
    print("Database siap")


if __name__ == "__main__":
    init_database()