from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Point to your WasteLess MySQL database:
DATABASE_URL = "mysql+pymysql://root:Abiodun001@localhost/wasteless"

# 2. Create the SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,               # Log SQL to the console (helpful while developing)
    pool_pre_ping=True       # Re-check connections, avoids “stale” errors
)

# 3. Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,        # You’ll manage transactions yourself
    autoflush=False,         # Don’t auto-flush pending changes before queries
    bind=engine
)

# 4. Base class for your ORM models
Base = declarative_base()
