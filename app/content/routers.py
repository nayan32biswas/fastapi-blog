from fastapi import APIRouter, Depends

from app.auth.dependencies import get_authenticated_user

from app.user.models import User
from .models import Content, Course, Article

router = APIRouter(prefix="/api")


@router.post("/v1/content/")
async def create_content(
    user: User = Depends(get_authenticated_user),
):
    content = Content(added_by_id=user.id, name="Demo Name").create()
    print(content)
    return "Content Added"


@router.post("/v1/course/")
async def create_course(
    user: User = Depends(get_authenticated_user),
):

    course = Course(
        added_by_id=user.id, name="Demo Name", description="Demo Content", title="Demo"
    ).create()
    print(course)
    return "Course Added"


@router.post("/v1/article/")
async def create_article(
    user: User = Depends(get_authenticated_user),
):
    content = Content(added_by_id=user.id, name="Name1").create()
    article = Article(content=content.id, description="Demo Content").create()
    print(article)
    return "Article Added"


@router.get("/v1/article/")
async def get_article():
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
        pipeline=[
            {"$addFields": {"content": {"$objectToArray": "$$ROOT.content"}}},
            {
                "$lookup": {
                    "from": Content._get_collection_name(),
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
