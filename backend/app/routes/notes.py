from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from firebase_admin import auth
from datetime import datetime

from backend.app.firebase_config import init_firebase

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

db = init_firebase()


class NoteCreate(BaseModel):
    title: str
    content: str


def get_user_from_token(authorization: str):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.replace("Bearer ", "")
        return auth.verify_id_token(token)

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("")
def create_note(note: NoteCreate, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    uid = user["uid"]

    note_data = {
        "uid": uid,
        "email": user.get("email"),
        "title": note.title,
        "content": note.content,
        "created_at": datetime.now().isoformat()
    }

    doc_ref = db.collection("notes").document()
    doc_ref.set(note_data)

    return {
        "message": "Note created successfully",
        "id": doc_ref.id,
        "note": note_data
    }


@router.get("")
def get_notes(authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    uid = user["uid"]

    docs = (
        db.collection("notes")
        .where("uid", "==", uid)
        .stream()
    )

    notes = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        notes.append(data)

    notes.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )

    return {
        "notes": notes
    } 
@router.put("/{note_id}")
def update_note(note_id: str, note: NoteCreate, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    uid = user["uid"]

    doc_ref = db.collection("notes").document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    data = doc.to_dict()

    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Not allowed")

    doc_ref.update({
        "title": note.title,
        "content": note.content,
        "updated_at": datetime.now().isoformat()
    })

    return {"message": "Note updated successfully"}


@router.delete("/{note_id}")
def delete_note(note_id: str, authorization: str = Header(None)):
    user = get_user_from_token(authorization)
    uid = user["uid"]

    doc_ref = db.collection("notes").document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    data = doc.to_dict()

    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Not allowed")

    doc_ref.delete()

    return {"message": "Note deleted successfully"}