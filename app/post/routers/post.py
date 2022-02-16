from datetime import datetime
from typing import Any, Optional, List


from fastapi import (
    Depends,
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    status,
    UploadFile,
)


from app.auth.dependencies import get_authenticated_user, has_post_delete_permission
from app.base.dependencies import get_db
from app.base.query import get_object_or_404
from app.base.utils.file import save_image
from app.user.models import User

from ..models import Comment, Post
from ..schemas import PostListOut, PostDetailsOut


router = APIRouter()


# @router.post(
#     "/api/v1/posts/",
#     response_model=PostOut,
#     status_code=status.HTTP_201_CREATED,
# )
# def post_create(
#     post: PostForm,
#     user: User = Depends(get_authenticated_user),
# ):
#     post = Post(**post.dict())
#     return post


@router.post("/api/v1/posts/", status_code=status.HTTP_201_CREATED)
def create_post(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    is_publish: bool = Form(False),
    image: UploadFile = File(None),
    user: User = Depends(get_authenticated_user),
    db: Any = Depends(get_db),
):
    raise NotImplementedError()
    image_path = save_image(image, folder="post")
    post = Post(
        user_id=user.id,
        name=name,
        description=description,
        published_at=published_at,
        is_publish=is_publish,
        image=image_path,
    ).create(db)
    post.save()
    return PostDetailsOut.from_orm(post)


@router.put("/api/v1/posts/{post_id}/")
def update_post(
    post_id: str,
    name: str = Form(None),
    description: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    is_publish: bool = Form(None),
    image: Optional[UploadFile] = None,
    user: User = Depends(get_authenticated_user),
    db: Any = Depends(get_db),
):
    post = get_object_or_404(db, Post, id=post_id)
    raise NotImplementedError()
    if user.id != post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    update_data = {}
    if image and image.filename:
        update_data["image"] = save_image(image, folder="post")
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if published_at is not None:
        update_data["published_at"] = published_at
    if is_publish is not None:
        update_data["is_publish"] = is_publish
    post.update(**update_data)
    post = get_object_or_404(db, Post, id=post_id)
    return PostDetailsOut.from_orm(post)


@router.get("/api/v1/posts/", status_code=status.HTTP_200_OK)
def fetch_posts(
    user_id: str = None,
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
    _: Optional[str] = Query(None, include_in_schema=False),
    db: Any = Depends(get_db),
):
    offset = (page - 1) * limit
    search_dict = {}
    order_by_dict = []
    if user_id:
        search_dict["user_id"] = user_id
    # if query is not None:
    #     search_dict["name__icontains"] = query
    if order_by:
        pass
    raise NotImplementedError()
    posts = (
        Post.find(db, search_dict)
        .order_by(order_by_dict)
        .skip(offset)
        .limit(limit)
        .select_related(max_depth=1)
        # .fields(comments=0)  # exclude comments field
    )
    return {"results": [PostListOut.from_orm(post) for post in posts]}


@router.get("/api/v1/posts/{post_id}/")
def fetch_post_details(post_id: str, db: Any = Depends(get_db)):
    post = get_object_or_404(db, Post, id=post_id)
    raise NotImplementedError()
    post.comments = [
        comment
        for comment in Comment.find(db, {"post_id": post_id}).select_related(max_depth=2)
    ]
    return PostDetailsOut.from_orm(post)


@router.delete(
    "/api/v1/posts/{post_id}/",
    status_code=status.HTTP_200_OK,
)
def delete_post(
    post_id: str,
    user: User = Depends(get_authenticated_user),
    db: Any = Depends(get_db),
):
    raise NotImplementedError()
    if has_post_delete_permission(user) is not True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post = get_object_or_404(db, Post, id=post_id, user_id=user.id)
    post.delete(db)
    return {"message": "Delete"}
