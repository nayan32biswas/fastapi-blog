from fastapi import APIRouter, Depends

from app.auth.dependencies import get_authenticated_user

from app.user.models import User
from .models import Content, Course, Article

router = APIRouter(prefix="/api")


@router.post("/v1/content/")
async def create_content(user: User = Depends(get_authenticated_user)):
    content = Content(added_by=user, name="Demo Name")
    content.save()
    return "Content Added"


@router.post("/v1/course/")
async def create_course(user: User = Depends(get_authenticated_user)):
    course = Course(added_by=user, name="Demo Name", content="Demo Content")
    course.save()
    return "Course Added"


@router.post("/v1/article/")
async def create_article(user: User = Depends(get_authenticated_user)):
    article = Article(added_by=user, name="Demo Name", content="Demo Content")
    article.save()
    return "Article Added"
