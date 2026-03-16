from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Ưu tiên DATABASE_URL để tránh hardcode secret trong source code
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
	DB_USER = os.getenv("POSTGRES_USER", "postgres")
	DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
	DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
	DB_PORT = os.getenv("POSTGRES_PORT", "5433")
	DB_NAME = os.getenv("POSTGRES_DB", "thai.nguyen")
	DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
