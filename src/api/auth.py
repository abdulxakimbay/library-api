# Python std lib
from datetime import datetime, timedelta, timezone

# Third party
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from ..config import settings
from ..db import get_session
from ..models import Librarian
from ..serializers import (AccessToken, RefreshToken, Tokens, LibrarianCreate, LibrarianLogin)

####################################################################################################
# SETTINGS
####################################################################################################

router = APIRouter(
    prefix="/auth",
    tags=["AUTH"]
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


####################################################################################################
# FUNCTIONS
####################################################################################################

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_refresh_token(data: dict) -> str:
    refresh_token_data = data.copy()
    refresh_token_data.update({
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    })
    return jwt.encode(refresh_token_data, settings.get_secret_key, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: dict) -> str:
    access_token_data = data.copy()
    access_token_data.update({
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    })
    return jwt.encode(access_token_data, settings.get_secret_key, algorithm=settings.JWT_ALGORITHM)


def create_tokens(data: dict) -> tuple[str, str]:
    return create_refresh_token(data), create_access_token(data)


async def authenticate_user(email: EmailStr, password: str, session: AsyncSession):
    result = await session.execute(select(Librarian).where(Librarian.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


####################################################################################################
# ENDPOINTS
####################################################################################################

@router.post("/sign-up")
async def sign_up(data: LibrarianCreate, session: AsyncSession = Depends(get_session)) -> Tokens:
    result = await session.execute(select(Librarian).where(Librarian.email == data.email))
    user: Librarian | None = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    hashed_password = hash_password(data.password)
    new_user = Librarian(email=data.email, password=hashed_password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    refresh_token, access_token = create_tokens({"sub": str(new_user.id)})
    return Tokens(refresh_token=refresh_token, access_token=access_token)


@router.post("/sign-in")
async def sign_in(data: LibrarianLogin, session: AsyncSession = Depends(get_session)) -> Tokens:
    incorrect_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )

    user: Librarian | None = await authenticate_user(data.email, data.password, session)
    if user is None:
        raise incorrect_credentials
    refresh_token, access_token = create_tokens({"sub": str(user.id)})
    return Tokens(refresh_token=refresh_token, access_token=access_token)


@router.post("/token")
async def login_for_access_token(refresh_token: RefreshToken) -> AccessToken:
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(refresh_token.refresh_token, settings.get_secret_key, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        type_: str | None = payload.get("type")
        if user_id is None or type_ != "refresh":
            raise invalid_credentials
        return AccessToken(access_token=create_access_token({"sub": user_id}))
    except InvalidTokenError:
        raise invalid_credentials
