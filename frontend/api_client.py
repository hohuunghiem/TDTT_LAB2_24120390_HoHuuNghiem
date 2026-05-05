import requests

API_BASE_URL = "http://localhost:8000"


def get_headers(id_token):
    return {
        "Authorization": f"Bearer {id_token}"
    }


def firebase_signup(api_key, email, password):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"

    response = requests.post(
        url,
        params={
            "key": api_key
        },
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
    )

    return response


def firebase_login(api_key, email, password):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

    response = requests.post(
        url,
        params={
            "key": api_key
        },
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
    )

    return response


def get_current_user(id_token):
    response = requests.get(
        f"{API_BASE_URL}/auth/me",
        headers=get_headers(id_token)
    )

    return response


def create_note(id_token, title, content):
    response = requests.post(
        f"{API_BASE_URL}/notes",
        headers=get_headers(id_token),
        json={
            "title": title,
            "content": content
        }
    )

    return response


def get_notes(id_token):
    response = requests.get(
        f"{API_BASE_URL}/notes",
        headers=get_headers(id_token)
    )

    return response
def update_note(id_token, note_id, title, content):
    return requests.put(
        f"{API_BASE_URL}/notes/{note_id}",
        headers=get_headers(id_token),
        json={
            "title": title,
            "content": content
        }
    )


def delete_note(id_token, note_id):
    return requests.delete(
        f"{API_BASE_URL}/notes/{note_id}",
        headers=get_headers(id_token)
    )

def reset_password(firebase_api_key, email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_api_key}"

    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email,
    }

    return requests.post(url, json=payload)