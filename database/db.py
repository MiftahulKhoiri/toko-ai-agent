""" database/db.py Koneksi database SQLite untuk toko-ai-agent """

from sqlalchemy import create_engine from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

Engine database 

engine = create_engine( DATABASE_URL, echo=False, future=True )

Session 

SessionLocal = sessionmaker( bind=engine, autoflush=False, autocommit=False )

Base model 

Base = declarative_base()

def get_session(): """ Membuat session database """ session = SessionLocal() try: yield session finally: session.close()

