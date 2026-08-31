import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite is useful for local development, but Vercel functions must use a
# persistent external database in production. Set DATABASE_URL in Vercel.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    if os.getenv("VERCEL"):
        raise RuntimeError(
            "DATABASE_URL is not configured. Set DATABASE_URL in the Vercel "
            "Production environment to your PostgreSQL/Supabase connection string."
        )
    DATABASE_URL = "sqlite:///./ai_platform.db"

# SQLAlchemy's plain PostgreSQL URL normally resolves to psycopg2. We ship
# psycopg v3, so explicitly select that driver when a standard PostgreSQL URL
# is supplied by Supabase or another hosted PostgreSQL provider.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
