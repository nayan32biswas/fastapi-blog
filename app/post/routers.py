from datetime import datetime
from typing import Optional, List

from fastapi import (
    Depends,
    APIRouter,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    status,
    UploadFile,
)

from app.auth.dependencies import get_authenticated_user
from app.user.models import User
from .models import Post
from .schemas import PostForm, PostOut


router = APIRouter()


@router.post(
    "/api/v1/posts/",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
)
def post_create(
    post: PostForm,
    user: User = Depends(get_authenticated_user),
):
    print(post)
    print(user)
    print(user.username)
    post = Post(**post.dict())
    return post


@router.post("/api/v1/posts-form/")
def post_create_with_form(
    image: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    number: int = Form(0),
):
    return {
        "image": image.filename,
        "name": name,
        "description": description,
        "published_at": published_at,
        "number": number,
    }


@router.get("/api/v1/posts/", status_code=status.HTTP_200_OK)
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


@router.get("/api/v1/posts/{post_id}")
def post_details(
    *,
    post_id: int = Path(0, ge=0, le=1000, title="Post ID"),
    query: str,
    user: User = Depends(get_authenticated_user),
):
    # By adding * you can order parameters
    print(user)
    if post_id == 0:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"id": post_id, "description": f"Post details of '{post_id}'"}


