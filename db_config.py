# db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# เชื่อมต่อ PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:mypassword@/postgres?host=/cloudsql/causal-relic-457214:g5:us-central1:kts-mini-db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
