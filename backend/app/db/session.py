import os
from typing import Generator
from sqlmodel import create_engine, Session

# Get the database URL from the environment, defaulting to the docker-compose setup
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://flowshield:flowshield_pass@localhost:5432/flowshield")

# Create the engine
engine = create_engine(DATABASE_URL, echo=False)

def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    with Session(engine) as session:
        yield session
