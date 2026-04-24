import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Render/Railway provide DATABASE_URL directly; fall back to individual vars for local Docker
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    engine = create_engine(DATABASE_URL)
else:
    DB_USER     = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_PORT     = os.getenv("DB_PORT", "5432")
    DB_NAME     = os.getenv("DB_NAME", "carinsurance_db")
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
