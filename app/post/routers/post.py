from datetime import datetime
from typing import Optional, List


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
from app.base.utils import get_object_or_404, save_image
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
    content: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    is_publish: bool = Form(False),
    image: UploadFile = File(None),
    user: User = Depends(get_authenticated_user),
):
    image_path = save_image(image, folder="post")
    post = Post(
        user=user,
        name=name,
        content=content,
        published_at=published_at,
        is_publish=is_publish,
        image=image_path,
    )
    post.save()
    return PostDetailsOut.from_orm(post)


@router.put("/api/v1/posts/{post_id}/")
def update_post(
    post_id: str,
    name: str = Form(None),
    content: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    is_publish: bool = Form(None),
    image: Optional[UploadFile] = None,
    user: User = Depends(get_authenticated_user),
):
    post = get_object_or_404(Post, id=post_id)
    if user != post.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    update_data = {}
    if image and image.filename:
        update_data["image"] = save_image(image, folder="post")
    if name is not None:
        update_data["name"] = name
    if content is not None:
        update_data["content"] = content
    if published_at is not None:
        update_data["published_at"] = published_at
    if is_publish is not None:
        update_data["is_publish"] = is_publish
    post.update(**update_data)
    post = get_object_or_404(Post, id=post_id)
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
    posts = (
        Post.objects(**search_dict)
        .order_by(order_by_dict)
        .skip(offset)
        .limit(limit)
        .select_related(max_depth=1)
        # .fields(comments=0)  # exclude comments field
    )
    return {"results": [PostListOut.from_orm(post) for post in posts]}


@router.get("/api/v1/posts/{post_id}/")
def fetch_post_details(post_id: str):
    post = get_object_or_404(Post, id=post_id)
    post.comments = [
        comment for comment in Comment.objects(post=post_id).select_related(max_depth=2)
    ]
    return PostDetailsOut.from_orm(post)


@router.delete(
    "/api/v1/posts/{post_id}/",
    status_code=status.HTTP_200_OK,
)
def delete_post(
    post_id: str,
    user: User = Depends(get_authenticated_user),
):
    if has_post_delete_permission(user) is not True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post = get_object_or_404(Post, id=post_id, user=user)
    post.delete()
    return {"message": "Delete"}
