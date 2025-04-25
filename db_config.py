# db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# เชื่อมต่อ PostgreSQL
DATABASE_URL = "postgresql://postgres:Sam219551624@34.132.113.178:5432/postgres"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
