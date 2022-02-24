from typing import Any
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_authenticated_user
from app.base.dependencies import get_db

from app.base.query import get_object_or_404
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
    # content = Content(added_by_id=user.id, name="Name1").create(db)
    content = get_object_or_404(db, Content, id="621727151f28b0780e948d1b")

    # article = Article(content=content, description="Demo Content").create(db)
    # print(article)

    for a in Article.find(db, {"content": content.ref}):
        print(a)
    return "Article Added"
