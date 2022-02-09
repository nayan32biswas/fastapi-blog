from fastapi import APIRouter


from . import comment, post


router = APIRouter()

router.include_router(post.router)
router.include_router(comment.router)
