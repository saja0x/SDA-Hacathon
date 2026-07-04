"""
ORM models. Each class here maps to a table in the database, and each
attribute maps to a column. SQLAlchemy translates between Python objects
and rows so we never write raw SQL by hand.
"""

from sqlalchemy import Column, Integer, String

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # unique=True puts a uniqueness constraint on the column, so the
    # database itself rejects duplicate emails -- not just our code.
    email = Column(String, unique=True, index=True, nullable=False)

    # We never store the actual password. Only the bcrypt hash goes in
    # the database. See auth.py for how hashing works.
    hashed_password = Column(String, nullable=False)

    # Role-based access control (RBAC) in its simplest form: a string
    # column that is either "user" or "admin". Routes that need admin
    # access check this value before letting the request through.
    role = Column(String, default="user", nullable=False)

    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
