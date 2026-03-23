# init_db.py
from database.config import Base, engine
from database.models import User

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
