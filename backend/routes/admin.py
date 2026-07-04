"""
Admin-only routes. Same idea as routes/users.py, but the dependency is
require_admin instead of get_current_user -- that's the entire
difference between "any logged-in user" and "admins only". A regular
user with a perfectly valid token gets a 403 from everything here.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    # The underscore name signals we only care about the side effect
    # (the role check), not the returned user object.
    _admin: models.User = Depends(require_admin),
):
    return db.query(models.User).all()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """
    A second admin route so the demo has more than one thing behind
    RBAC. Counts accounts by role using two simple ORM queries.
    """
    return {
        "total_users": db.query(models.User).count(),
        "admins": db.query(models.User).filter(models.User.role == "admin").count(),
        "regular_users": db.query(models.User).filter(models.User.role == "user").count(),
    }
