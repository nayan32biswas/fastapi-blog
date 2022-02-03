from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from mongoengine import connect

from app.base import routers as base_routers
from app.auth import routers as auth_routers
from app.user import routers as user_routers
from app.post import routers as post_routers
from app.content import routers as content_routers

from app.base.exception_handler import UnicornException, unicorn_exception_handler
from app.base.middleware import add_process_time_header

from app.base.config import ALLOWED_HOSTS
from app.base.config import DB_URL

app = FastAPI()
# Global dependency
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

connect(host=DB_URL)


app.include_router(base_routers.router, tags=["default"])
app.include_router(auth_routers.router, tags=["auth"])
app.include_router(user_routers.router, tags=["user"])
app.include_router(post_routers.router, tags=["post"])
app.include_router(content_routers.router, tags=["content"])

# Exception handler
app.add_exception_handler(UnicornException, unicorn_exception_handler)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
