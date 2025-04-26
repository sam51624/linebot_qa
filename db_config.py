from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ใช้ Public IP แทน Unix socket
DATABASE_URL = "postgresql+psycopg2://postgres:Sam219551624@34.132.113.178:5432/postgres"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
