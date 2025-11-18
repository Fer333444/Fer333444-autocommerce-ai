import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Leer de NEON_DATABASE_URL en lugar de DATABASE_URL
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

if not DATABASE_URL:
    raise Exception("NEON_DATABASE_URL is missing")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
