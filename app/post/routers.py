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


from app.auth.dependencies import get_authenticated_user, has_post_delete_permission
from app.base.utils import get_object_or_404, save_image
from app.user.models import User

from .models import Comment, EmbeddedComment, Post
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
    post.comments = [comment for comment in Comment.objects(post=post_id)]
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


@router.post("/api/v1/posts/{post_id}/", response_model=CommentOut)
def create_post_comment(
    post_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    post = get_object_or_404(Post, id=post_id)
    comment = Comment(user=user, post=post, content=content)
    comment.save()

    return comment


@router.put("/api/v1/posts/{post_id}/{comment_id}/")
def update_comment(
    post_id: str,
    comment_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    comment = get_object_or_404(Comment, id=comment_id, post=post_id, user=user)
    comment.content = content
    comment.updated_at = datetime.utcnow()
    comment.save()
    comment.reload()

    return CommentOut.from_orm(comment)


@router.delete(
    "/api/v1/posts/{post_id}/{comment_id}/",
    status_code=status.HTTP_200_OK,
)
def delete_comment(
    post_id: str,
    comment_id: str,
    user: User = Depends(get_authenticated_user),
):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post=post_id,
        user=user,
    )
    comment.delete()

    return {"message": "Delete"}


@router.post(
    "/api/v1/posts/{post_id}/{comment_id}/child/",
    response_model=CommentOut,
)
def create_child_comment(
    post_id: str,
    comment_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    comment = get_object_or_404(Comment, id=comment_id, post=post_id, user=user)
    child_comment = EmbeddedComment(user=user, content=content)
    comment.update(push__childs=child_comment)
    return CommentOut.from_orm(child_comment)


@router.put(
    "/api/v1/posts/{post_id}/{comment_id}/child/{child_comment_id}/",
    status_code=status.HTTP_200_OK,
    response_model=CommentOut,
)
def update_child_comment(
    post_id: str,
    comment_id: str,
    child_comment_id: str,
    content: str = Form(...),
    user: User = Depends(get_authenticated_user),
):
    _ = get_object_or_404(
        Comment,
        id=comment_id,
        post=post_id,
        childs__user=user,
        childs__id=child_comment_id,
    )

    # Comment.objects(
    #     __raw__={
    #         "_id": ObjectId(comment_id),
    #         "post": ObjectId(post_id),
    #         "childs": {"$elemMatch": {"id": ObjectId(child_comment_id)}},
    #     }
    # ).update_one(
    #     __raw__={
    #         "$set": {
    #             "childs.$.content": content,
    #             "childs.$.updated_at": datetime.utcnow(),
    #         }
    #     }
    # )
    """As equivalent as __raw__ query"""
    Comment.objects(id=comment_id, post=post_id, childs__id=child_comment_id).update(
        set__childs__S__content=content,
        set__childs__S__updated_at=datetime.utcnow(),
    )

    comment = Comment.objects(id=comment_id).aggregate(
        [
            {"$match": {"childs.id": ObjectId(child_comment_id)}},
            {
                "$project": {
                    "childs": {
                        "$filter": {
                            "input": "$childs",
                            "as": "comment",
                            "cond": {"$eq": ["$$comment.id", ObjectId(child_comment_id)]},
                        },
                    },
                },
            },
        ]
    )
    comment_out = None
    for c in comment:
        try:
            comment_out = c["childs"][0]
            comment_out["user"] = user
        except Exception:
            pass
        break
    return comment_out


@router.delete(
    "/api/v1/posts/{post_id}/{comment_id}/child/{child_comment_id}/",
    status_code=status.HTTP_200_OK,
)
def delete_child_comment(
    post_id: str,
    comment_id: str,
    child_comment_id: str,
    user: User = Depends(get_authenticated_user),
):
    _ = get_object_or_404(
        Comment,
        id=comment_id,
        post=post_id,
        childs__user=user,
        childs__id=child_comment_id,
    )

    Comment.objects(id=comment_id, post=post_id).update(
        pull__childs__id=child_comment_id,
    )

    return {"message": "Delete"}


# comment = Comment.objects(
#     __raw__={
#         "_id": ObjectId(comment_id),
#         "childs": {"$elemMatch": {"id": ObjectId(first_comment_id)}},
#     }
# ).filter(__raw__={"childs": {"$elemMatch": {"id": ObjectId(first_comment_id)}}})
"""mongodb 4 or letter deprecated $eval command"""
# data = Comment.objects.exec_js(
#     """
#     function() {
#         var comments = [];
#         return comments;
#     }
#     """
# )
