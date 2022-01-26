from datetime import datetime
from typing import Optional, List

from fastapi import (
    Cookie,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    status,
    UploadFile,
)
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field


class PostIn(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    description: Optional[str] = None
    published_at: datetime = None
    number: int = 0


class PostOut(PostIn):
    id: int = None


class PostForm(PostIn):
    image: UploadFile = File(...)


app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def home(cookie: Optional[str] = Cookie(None), user_agent: Optional[str] = Header(None)):
    return {
        "message": "Hello World",
        "cookie": cookie,
        "User-Agent": user_agent,
    }


@app.post("/api/v1/posts/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def post_create(post: PostIn):
    return post


@app.post("/api/v1/posts-form/")
def post_create_with_form(
    image: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    published_at: datetime = Form(None),
    number: int = Form(0),
):
    return {
        "image": image.filename,
        "name": name,
        "description": description,
        "published_at": published_at,
        "number": number,
    }


# @app.post("/api/v1/posts-form/")
# def post_create_with_form(post: PostForm):
#     return {"image": "form"}


@app.get("/api/v1/posts/", status_code=status.HTTP_200_OK)
def posts(
    user_id: int = None,
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
    hidden_query: Optional[str] = Query(None, include_in_schema=False),
):
    return {
        "params": f"user_id={user_id}, query={query}, limit={limit}, page={page}, order_by={order_by}, hidden_query={hidden_query}",
    }


@app.get("/api/v1/posts/{post_id}")
def post_details(*, post_id: int = Path(0, ge=0, le=1000, title="Post ID"), query: str):
    # By adding * you can order parameters
    if post_id == 0:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"id": post_id, "description": f"Post details of '{post_id}'"}


@app.post("/upload-image/")
async def create_upload_file(file: UploadFile = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
