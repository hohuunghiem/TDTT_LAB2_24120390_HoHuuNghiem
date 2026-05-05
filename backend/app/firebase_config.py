import firebase_admin
from firebase_admin import credentials, firestore


def load_secrets():
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    with open(".streamlit/secrets.toml", "rb") as file:
        return tomllib.load(file)


def init_firebase():
    if firebase_admin._apps:
        return firestore.client()

    secrets = load_secrets()

    cred = credentials.Certificate(dict(secrets["firebase_admin"]))
    firebase_admin.initialize_app(cred)

    return firestore.client()