from fastapi import FastAPI, Header, HTTPException
from firebase_admin import auth

from backend.app.routes.notes import router as notes_router
from backend.app.routes.google_auth import router as google_auth_router

app = FastAPI(
    title="Note App API",
    description="FastAPI backend for Note App with Firebase and Google Cloud OAuth",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Note App API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/auth/me")
def auth_me(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.replace("Bearer ", "")
        decoded = auth.verify_id_token(token)

        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
            "name": decoded.get("name")
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


app.include_router(notes_router)
app.include_router(google_auth_router)