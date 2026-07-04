"""
Public auth routes: register and login. These are the only endpoints in
the app that don't require a token -- they're how you GET a token.

APIRouter works like a mini FastAPI app. We define routes on it here,
then main.py plugs it in with app.include_router(). The prefix means
every path in this file automatically starts with /auth, and the tag
groups these endpoints together in the /docs UI.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    By the time this function runs, FastAPI has already validated the
    body against UserCreate -- bad email format or short password never
    make it this far.
    """
    # The email column is unique, but checking first lets us return a
    # friendly 400 instead of a raw database error.
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = models.User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
    )

    # The classic ORM write pattern: add stages the object, commit
    # writes it, refresh pulls back database-generated values (the id).
    db.add(user)
    db.commit()
    db.refresh(user)

    # We return the ORM object directly; response_model=UserOut converts
    # it and strips anything not in the schema (like hashed_password).
    return user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    # Same error whether the email doesn't exist or the password is
    # wrong. Saying "email not found" would let attackers probe which
    # emails have accounts.
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return schemas.Token(access_token=create_access_token(user))
