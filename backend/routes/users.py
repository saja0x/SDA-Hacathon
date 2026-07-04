"""
Routes for logged-in users. Every endpoint here depends on
get_current_user, so a missing/invalid token means a 401 before any of
these functions run. Role doesn't matter -- a regular user and an admin
can both call these.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    """
    Depends(get_current_user) is the entire protection mechanism. No
    valid token in the Authorization header -> the dependency raises a
    401 and this function never runs.
    """
    return current_user


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    update_data: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile information."""
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.phone is not None:
        current_user.phone = update_data.phone
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/profile")
def read_profile(current_user: models.User = Depends(get_current_user)):
    """
    A second protected route, mostly to show that protecting an
    endpoint is the same one-liner every time. This one returns a plain
    dict instead of a schema -- FastAPI serializes it to JSON as-is.
    """
    return {
        "message": f"Hello {current_user.email}, this came from a protected endpoint.",
        "your_role": current_user.role,
        "tip": "Open DevTools > Network and look at the Authorization header on this request.",
    }
