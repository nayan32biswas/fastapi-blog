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
    content = Content(added_by_id=user.id, name="Demo Name").create(db)
    course = Course(content_id=content.id, description="Demo Content").create(db)
    print(course)
    return "Course Added"


@router.post("/v1/article/")
async def create_article(
    user: User = Depends(get_authenticated_user), db: Any = Depends(get_db)
):
    content = Content(added_by_id=user.id, name="Demo Name").create(db)
    article = Article(content_id=content.id, description="Demo Content").create(db)
    print(article)
    return "Article Added"
