from datetime import datetime
from typing import Optional, List

from fastapi import Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    description: Optional[str] = None
    published_at: datetime = None
    number: int = 0

    # @property
    # def is_published(self) -> bool:
    #     return self.published_at is not None


app = FastAPI()


@app.get("/")
def home(cookie: Optional[str] = Cookie(None), user_agent: Optional[str] = Header(None)):
    return {
        "message": "Hello World",
        "cookie": cookie,
        "User-Agent": user_agent,
    }


@app.post("/api/v2/posts/")
def post_create(post: PostCreate):
    demo = post.name + post.number
    print(demo)
    return post


@app.get("/api/v2/posts/")
def posts(
    user_id: int = None,
    limit: int = 10,
    page: int = 1,
    query: Optional[str] = Query(
        None,
        min_length=5,
        max_length=10,
        regex="^post.*$",
        title="Query string",
        alias="q",
    ),
    order_by: Optional[List[str]] = Query(
        ["key", "direction"],
        max_length=10,
        deprecated=True,
    ),
    hidden_query: Optional[str] = Query(None, include_in_schema=False),
):
    return {
        "params": f"user_id={user_id}, query={query}, limit={limit}, page={page}, order_by={order_by}, hidden_query={hidden_query}",
    }


@app.get("/api/v2/posts/{post_id}")
def post_details(*, post_id: int = Path(0, ge=1, le=1000, title="Post ID"), query: str):
    # By adding * you can order parameters
    return {"id": post_id, "description": f"Post details of '{post_id}'"}
