"""
All the security plumbing: password hashing, JWT creation/verification,
and the FastAPI dependencies that protect routes. The files in routes/
import from here -- this module defines HOW auth works, the routers
decide WHERE it gets applied.

The flow looks like this:

  register -> we hash the password and store the user
  login    -> we verify the password and hand back a signed JWT
  any protected route -> client sends "Authorization: Bearer <token>",
                         get_current_user decodes it and loads the user
  admin route -> require_admin runs get_current_user first, then also
                 checks the role column
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# In production this comes from an environment variable, never source
# code -- anyone who has this key can forge tokens for any user.
SECRET_KEY = "change-me-in-production-this-is-a-classroom-demo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# HTTPBearer pulls the token out of the "Authorization: Bearer xxx"
# header for us and returns 403 if the header is missing.
bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    bcrypt is a one-way hash designed for passwords: it's deliberately
    slow (to make brute-forcing expensive) and salts automatically (so
    two users with the same password get different hashes).
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """
    You can't "decrypt" a bcrypt hash. Instead, checkpw hashes the
    attempt with the same salt and compares the results.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(user: User) -> str:
    """
    A JWT is three base64 chunks: header.payload.signature. The payload
    (our "claims") is readable by anyone -- paste a token into jwt.io
    and look -- so never put secrets in it. What makes it secure is the
    signature: it's computed with SECRET_KEY, so if anyone tampers with
    the payload the signature stops matching and we reject the token.
    """
    payload = {
        # "sub" (subject) is the standard claim for "who this token is
        # about". The spec wants it to be a string.
        "sub": str(user.id),
        # We bake the role in so the frontend can show/hide admin UI
        # without an extra request. The backend still re-checks the role
        # against the database on every admin call -- never trust the
        # client alone.
        "role": user.role,
        # "exp" is enforced by jwt.decode(): an expired token raises an
        # exception, no extra code needed on our side.
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Route dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for any route that requires a logged-in user. Decodes the
    token, then loads the user from the database. If anything is off --
    bad signature, expired, user deleted since the token was issued --
    the request stops here with a 401.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        # Part of the HTTP spec for 401s: tells the client what auth
        # scheme the server expects.
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # decode() verifies the signature AND the exp claim in one call.
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise unauthorized

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise unauthorized

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    RBAC happens here. This dependency chains on top of get_current_user
    (so the token check already passed), then adds one more rule: the
    role must be "admin". 401 means "we don't know who you are";
    403 means "we know who you are, and you're not allowed".
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
