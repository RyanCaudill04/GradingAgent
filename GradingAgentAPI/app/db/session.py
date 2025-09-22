from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

if settings.DATABASE_URL_USED.startswith("postgresql"):
    import psycopg2

engine = create_engine(str(settings.DATABASE_URL_USED), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
