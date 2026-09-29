from .database import Base, engine
from . import models


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    print("NEXUS PostgreSQL schema initialized.")


if __name__ == "__main__":
    initialize_database()