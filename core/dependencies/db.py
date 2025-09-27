from typing import Generator, Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from core.db import Session as SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
