from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.base import routers as base_routers
from app.auth import routers as auth_routers
from app.odm.connection import connect, disconnect
from app.user import routers as user_routers
from app.post import routers as post_routers
from app.content import routers as content_routers

from app.base.exception_handler import UnicornException, unicorn_exception_handler
from app.base.middleware import add_process_time_header

from app.base import config

app: Any = FastAPI()
# Global dependency
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

config.init_firebase_auth()


@app.on_event("startup")
async def startup_db_client():
    connect(config.DB_URL)
    print("db connected")


@app.on_event("shutdown")
async def shutdown_db_client():
    disconnect()
    print("db disconnected")


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
    allow_origins=config.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)


if __name__ == "__main__":
    try:
        """CLI"""
        from app.cli import cli_app

        connect(config.DB_URL)
        cli_app()
    finally:
        disconnect()
