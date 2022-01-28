import os

from app.base.utils import comma_separated_str_to_list


SECRET_KEY = os.environ.get("SECRET_KEY", "long-long-long-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

DB_URL = os.environ.get("MONGO_HOST", "mongodb://root:example@db:27017/")

ALLOWED_HOSTS = comma_separated_str_to_list(
    os.environ.get("ALLOWED_HOSTS", "http://localhost:8080")
)
