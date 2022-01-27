from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware

from . import routers as app_routers
from .auth import routers as auth_routers
from .user import routers as user_routers
from .post import routers as post_routers

from .database import connect_to_db
print(connect_to_db)

app = FastAPI()
# Global dependency
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

app.include_router(app_routers.router)
app.include_router(auth_routers.router, tags=["auth"])
app.include_router(user_routers.router, tags=["user"])
app.include_router(post_routers.router, tags=["post"])

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
