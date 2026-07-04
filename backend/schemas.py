"""
Pydantic schemas. These define the shape of the JSON our API accepts and
returns. FastAPI uses them to validate incoming requests (bad data gets
rejected with a 422 before our code even runs) and to serialize
responses.

Schemas are NOT the same as the ORM models in models.py. Models describe
database tables; schemas describe API payloads. Keeping them separate
lets us, for example, accept a plain-text password on the way in but
never expose the hashed password on the way out.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    """Body of POST /auth/register."""

    # EmailStr validates the format for us -- "notanemail" gets a 422.
    email: EmailStr

    # Field(min_length=...) is basic input validation. Real apps would
    # enforce more, but one rule is enough to show the concept.
    password: str = Field(min_length=6)

    # Literal restricts the value to exactly these two strings.
    # A role dropdown at registration is obviously not how you'd assign
    # admins in production (anyone could pick "admin") -- it's here so
    # the RBAC demo is easy to try out.
    role: Literal["user", "admin"] = "user"


class UserLogin(BaseModel):
    """Body of POST /auth/login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Body of PUT /users/me."""
    full_name: str | None = None
    phone: str | None = None

class UserOut(BaseModel):
    """
    What we send back when returning a user. Note there's no password
    field of any kind -- this is the whole point of a response schema.
    """

    id: int
    email: EmailStr
    role: str
    full_name: str | None = None
    phone: str | None = None

    # from_attributes lets Pydantic build this schema straight from a
    # SQLAlchemy User object (it reads user.id, user.email, etc.)
    # instead of requiring a dict.
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Response of POST /auth/login: the JWT plus its type."""

    access_token: str
    token_type: str = "bearer"
