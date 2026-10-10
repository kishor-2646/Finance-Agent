"""Run once (safe to re-run): creates the tables and a demo user."""
from sqlalchemy import inspect, select

from db import Base, SessionLocal, User, engine

Base.metadata.create_all(engine)

with SessionLocal() as db:
    if not db.scalar(select(User).where(User.id == 1)):
        db.add(User(id=1, email="demo@example.com"))
        db.commit()
        print("Created demo user (id=1)")

print("Tables:", sorted(inspect(engine).get_table_names()))