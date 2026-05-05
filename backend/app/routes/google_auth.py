from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from firebase_admin import auth
import requests
import urllib.parse

from backend.app.firebase_config import load_secrets, init_firebase

router = APIRouter(
    prefix="/auth/google",
    tags=["google-auth"]
)

init_firebase()


@router.get("/start")
def google_login_start():
    secrets = load_secrets()
    google_config = secrets["google_login"]

    params = {
        "client_id": google_config["google_client_id"],
        "redirect_uri": google_config["google_redirect_uri"],
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    google_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode(params)
    )

    return RedirectResponse(google_url)


@router.get("/callback")
def google_login_callback(code: str):
    secrets = load_secrets()
    google_config = secrets["google_login"]

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": google_config["google_client_id"],
            "client_secret": google_config["google_client_secret"],
            "redirect_uri": google_config["google_redirect_uri"],
            "grant_type": "authorization_code"
        }
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Cannot get Google access token"
        )

    access_token = token_response.json()["access_token"]

    user_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if user_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Cannot get Google user information"
        )

    google_user = user_response.json()

    google_id = google_user["id"]
    email = google_user.get("email", "")
    name = google_user.get("name", "")

    firebase_uid = f"google_{google_id}"

    custom_token = auth.create_custom_token(
        firebase_uid,
        {
            "email": email,
            "name": name,
            "provider": "google"
        }
    ).decode("utf-8")

    firebase_response = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken",
        params={
            "key": google_config["firebase_web_api_key"]
        },
        json={
            "token": custom_token,
            "returnSecureToken": True
        }
    )

    if firebase_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Cannot exchange custom token for Firebase ID token"
        )

    firebase_data = firebase_response.json()
    id_token = firebase_data["idToken"]

    frontend_url = google_config["frontend_url"]

    redirect_url = (
        f"{frontend_url}"
        f"?id_token={urllib.parse.quote(id_token)}"
        f"&email={urllib.parse.quote(email)}"
        f"&name={urllib.parse.quote(name)}"
    )

    return RedirectResponse(redirect_url)