from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# URL de Neon (desde tu .env)
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
