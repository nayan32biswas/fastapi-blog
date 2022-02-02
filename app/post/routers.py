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

from bson.objectid import ObjectId


from app.auth.dependencies import get_authenticated_user
from app.base.utils import get_object_or_404, save_image
from app.user.models import User

from .models import Comment, Post
from .schemas import CommentOut, PostListOut, PostDetailsOut


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


@router.post(
    "/api/v1/posts/", response_model=PostDetailsOut, status_code=status.HTTP_201_CREATED
)
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
    return post._data


@router.put("/api/v1/posts/{post_id}/", response_model=PostDetailsOut)
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
    return post._data


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
        .fields(comments=0)  # exclude comments field
        .select_related(max_depth=1)
    )
    return {"results": [PostListOut.from_orm(post) for post in posts]}


@router.get("/api/v1/posts/{post_id}/", response_model=PostDetailsOut)
def fetch_post_details(post_id: str):
    post = get_object_or_404(Post, id=post_id)
    return post


@router.post("/api/v1/posts/{post_id}/", response_model=CommentOut)
def create_post_comment(
    post_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    post = get_object_or_404(Post, id=post_id)
    comment = Comment(user=user, content=content)
    post.update(push__comments=comment)
    # Post.objects(id=post_id).update_one(push__comments=comment)
    comment.user = user
    return comment


@router.put("/api/v1/posts/{post_id}/{comment_id}/")
def update_comment(
    post_id: str,
    comment_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    _ = get_object_or_404(
        Post, id=post_id, comments__match={"id": comment_id, "user": user.id}
    )

    Post.objects(
        __raw__={
            "_id": ObjectId(post_id),
            "comments": {"$elemMatch": {"id": ObjectId(comment_id)}},
        }
    ).update_one(
        __raw__={
            "$set": {
                "comments.$.content": content,
                "comments.$.timestamp": datetime.utcnow(),
            }
        }
    )
    # comment = Post.objects(__raw__={"_id": ObjectId(post_id)}).filter(
    #     __raw__={"comments": {"$elemMatch": {"id": ObjectId(comment_id)}}}
    # )

    # data = Post.objects.exec_js(
    #     """
    #     function(text) {
    #         var comments = [];
    #         return comments;
    #     }
    #     """
    # )
    # print(data)

    # comment = Post.objects(id=post_id).fields(name=1, comments=0).first()
    # print("comment: ", comment._data)

    return "Updated Comment"


@router.post("/api/v1/posts/{post_id}/child/", response_model=CommentOut)
def create_child_comment(
    post_id: str,
    comment_ids: List[str] = Query(...),
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    print(comment_ids)
    post = get_object_or_404(Post, id=post_id)
    comment = Comment(user=user, content=content)

    post.update(**{"set__comments": comment})
    # comment.user = user
    return comment
