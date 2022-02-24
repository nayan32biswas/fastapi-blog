from typing import Any
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_authenticated_user
from app.base.dependencies import get_db

from app.user.models import User
from .models import Content, Course, Article

router = APIRouter(prefix="/api")


@router.post("/v1/content/")
async def create_content(
    user: User = Depends(get_authenticated_user), db: Any = Depends(get_db)
):
    content = Content(added_by_id=user.id, name="Demo Name").create(db)
    print(content)
    return "Content Added"


@router.post("/v1/course/")
async def create_course(
    user: User = Depends(get_authenticated_user), db: Any = Depends(get_db)
):

    course = Course(
        added_by_id=user.id, name="Demo Name", description="Demo Content"
    ).create(db)
    print(course)
    return "Course Added"


@router.post("/v1/article/")
async def create_article(
    user: User = Depends(get_authenticated_user), db: Any = Depends(get_db)
):
    content = Content(added_by_id=user.id, name="Name1").create(db)
    article = Article(content=content, description="Demo Content").create(db)
    print(article)
    return "Article Added"


@router.get("/v1/article/")
async def get_article(db: Any = Depends(get_db)):
    """
    # Get related data with ObjectId
    for a in Content.aggregate(
        db,
        pipeline=[
            {
                "$lookup": {
                    "from": "user",
                    "localField": "added_by_id",
                    "foreignField": "_id",
                    "as": "user",
                }
            }
        ],
    ):
        print(a)
    """
    articles = []

    for a in Article.aggregate(
        db,
        pipeline=[
            {"$addFields": {"content": {"$objectToArray": "$$ROOT.content"}}},
            {
                "$lookup": {
                    "from": Content._db(),
                    "localField": "content.1.v",
                    "foreignField": "_id",
                    "as": "content",
                }
            },
        ],
    ):
        print(a)
        articles.append(a)
    return []
