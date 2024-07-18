from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///test.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
