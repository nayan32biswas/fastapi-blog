from datetime import timedelta
import os
from pathlib import Path

from .config_utils import comma_separated_str_to_list, parse_redis_url


SECRET_KEY = os.environ.get("SECRET_KEY", "long-long-long-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
REFRESH_TOKEN_EXPIRE_DAYS = 30

DB_URL = os.environ.get("MONGO_HOST", "mongodb://root:example@db:27017/test")

ALLOWED_HOSTS = comma_separated_str_to_list(
    os.environ.get("ALLOWED_HOSTS", "http://localhost:8080")
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

REDIS_URL = os.environ.get("REDIS_HOST", "localhost://redis:6379/0")
REDIS_CONNECTION_CONFIG = parse_redis_url(REDIS_URL)
REDIS_DEFAULT_TIMEOUT = timedelta(hours=1)

FIREBASE_ACCOUNT_CREDENTIAL_PATH = os.environ.get(
    "FIREBASE_ACCOUNT_CREDENTIAL_PATH", None
)


def init_firebase_auth():
    import firebase_admin

    if FIREBASE_ACCOUNT_CREDENTIAL_PATH is None:
        raise Exception("Firebase Credintial is not provided")

    FIREBASE_ACCOUNT_CREDENTIALS = os.path.join(
        BASE_DIR, FIREBASE_ACCOUNT_CREDENTIAL_PATH
    )

    if os.path.exists(FIREBASE_ACCOUNT_CREDENTIALS) is False:
        raise Exception("Invalid Firebase Credintial path")

    try:
        cred = firebase_admin.credentials.Certificate(FIREBASE_ACCOUNT_CREDENTIALS)
        firebase_admin.initialize_app(credential=cred)
        print("\tFirebase init")
    except Exception as e:
        print(f"\tFirebase init error: {e}")
