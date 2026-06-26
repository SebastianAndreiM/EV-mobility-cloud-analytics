"""Shared SQLAlchemy declarative base. Imported by every model and by both
the async (FastAPI) and sync (Celery) engines so metadata stays consistent.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
