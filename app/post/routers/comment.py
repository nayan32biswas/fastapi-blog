from datetime import datetime


from fastapi import (
    Depends,
    APIRouter,
    Form,
    status,
)

from bson.objectid import ObjectId


from app.auth.dependencies import get_authenticated_user
from app.base.query import get_object_or_404
from app.user.models import User

from ..models import Comment, EmbeddedComment, Post
from ..schemas import CommentOut


router = APIRouter()


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
