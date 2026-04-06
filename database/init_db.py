""" database/init_db.py Membuat database dan tabel """

from database.db import engine from database.models import Base

def init_database(): print("Membuat database...")

Base.metadata.create_all(bind=engine) print("Database siap") 

if name == "main": init_database()

