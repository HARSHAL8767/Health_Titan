from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="postgresql://postgres:harshal@localhost/health_tracker"

engine=create_engine(DATABASE_URL)

sessionLocal=sessionmaker(
    bind = engine
)

Base=declarative_base()

#database session
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

