# Full-Stack Auth Demo: JWT + RBAC

A minimal example of token-based authentication across a full stack:

- **Backend:** FastAPI + SQLAlchemy ORM (SQLite) + Pydantic + PyJWT, served by Uvicorn
- **Frontend:** React (Vite) + react-router-dom with `BrowserRouter` and protected routes

Features, on purpose, are limited to exactly three things:

1. Register / log in with a JWT access token
2. A protected page any logged-in user can see (`/dashboard`)
3. An admin-only page enforced by role-based access control (`/admin`)

## Running it

Two terminals.

**Backend** (http://localhost:8000):

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend** (http://localhost:5173):

```
cd frontend
npm install
npm run dev
```

## Trying the RBAC demo

1. Register an account with role **user** -- you can see `/dashboard` but get redirected away from `/admin` (and the API returns 403 if called directly).
2. Log out, register a second account with role **admin** -- the Admin link appears and `/admin` lists every registered user.

The role dropdown at registration is for classroom convenience only; a real app would never let users choose their own role.

## Where to look

| Concept | File |
| --- | --- |
| Engine / session / `get_db` dependency | `backend/database.py` |
| ORM model (the `users` table) | `backend/models.py` |
| Pydantic request/response schemas | `backend/schemas.py` |
| Hashing, JWT, `get_current_user`, `require_admin` | `backend/security.py` |
| App setup, CORS, router wiring | `backend/main.py` |
| Public routes (register, login) | `backend/routes/auth.py` |
| Protected routes (`/users/me`, `/users/profile`) | `backend/routes/users.py` |
| Admin-only routes (`/admin/users`, `/admin/stats`) | `backend/routes/admin.py` |
| Auth state shared via context | `frontend/src/AuthContext.jsx` |
| Frontend route guard | `frontend/src/components/ProtectedRoute.jsx` |
| Router setup | `frontend/src/App.jsx` |

The API also self-documents at http://localhost:8000/docs once the backend is running.
