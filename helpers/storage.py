from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///projects.db", echo=False, query_cache_size=0)
SESSION = sessionmaker()
SESSION.configure(bind=engine)

BASE = declarative_base()
