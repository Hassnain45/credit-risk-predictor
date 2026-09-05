import os
import sys
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# On Windows (Local Dev): Use project root database
# On Linux (Streamlit Cloud): Use /tmp directory where the OS guarantees full read/write permissions
if sys.platform.startswith("win"):
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credit_underwriting.db"))
else:
    DB_PATH = os.path.join(tempfile.gettempdir(), "credit_underwriting.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()