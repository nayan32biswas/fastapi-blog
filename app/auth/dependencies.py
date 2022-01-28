from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.base.config import (
    SECRET_KEY,
    ALGORITHM,
)
from app.user.models import User
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_authenticated_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_authenticated_user(token_data: User = Depends(get_authenticated_token)):
    user = User.objects(username=token_data.username).first()
    if user is None:
        raise credentials_exception
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
