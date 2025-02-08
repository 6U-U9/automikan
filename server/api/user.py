from pydantic import BaseModel
class UserCreateInput(BaseModel):
    name: str
    password: str
    email: str | None = None

class UserOutput(BaseModel):
    name: str

class UserUpdateInput(BaseModel):
    name: str
    old_password: str | None = None
    password: str | None = None
    email: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from manager.global_manager import GlobalManager
from storage.model import User
from api.database import get_database
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

unauthorized_exception = HTTPException(
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = "Could not validate credentials",
    headers = {"WWW-Authenticate": "Bearer"},
)

def _authenticate(username: str, password: str) -> User | None:
    user: User | None = User.get_or_none(User.name == username)
    if not user:
        return None
    if not hashlib.sha256(password.encode("utf-8")).hexdigest() == user.password:
        return None
    return user

def _create_access_token(data: dict, expire: datetime | None = None):
    encode_data = data.copy()
    if not expire:
        expire = datetime.now(timezone.utc) + timedelta(days = 7)
    encode_data.update({"exp": expire})
    encoded_jwt = jwt.encode(encode_data, GlobalManager.global_config.jwt_secret_key, algorithm = GlobalManager.global_config.jwt_algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, GlobalManager.global_config.jwt_secret_key, algorithms = [GlobalManager.global_config.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise unauthorized_exception
    except jwt.PyJWTError:
        raise unauthorized_exception
    user: User | None = User.get_or_none(User.name == username)
    if user is None:
        raise unauthorized_exception
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = _authenticate(form_data.username, form_data.password)
    if not user:
        raise unauthorized_exception
    access_token_expire = datetime.now(timezone.utc) + timedelta(minutes = 30)
    access_token = _create_access_token(
        data = {"sub": user.name}, expire = access_token_expire
    )
    return {"access_token": access_token, "token_type": "bearer", "expire_time": int(access_token_expire.timestamp())}

@router.get("/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    return {"name": current_user.name, "email": current_user.email}

@router.get("/create", response_model = UserOutput)
def create_user(item: UserCreateInput, current_user: User = Depends(get_current_user)):
    user, create = User.get_or_create(
        name = item.name,
        defaults = {
            "password": hashlib.sha256(item.password.encode("utf-8")).hexdigest(),
            "email" : item.email if item.email != None else ""
        }
    )
    if not create:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Duplicate username",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    return {"name": user.name}

@router.get("/password", response_model = UserOutput)
def update_password(item: UserUpdateInput, current_user: User = Depends(get_current_user)):
    user: User | None = User.get_or_none(User.name == item.name)
    if user is None:
        raise unauthorized_exception
    if not item.old_password or hashlib.sha256(item.old_password.encode("utf-8")).hexdigest() != user.password:
        raise unauthorized_exception
    if not item.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "New password is empty",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    user.password = hashlib.sha256(item.password.encode("utf-8")).hexdigest()
    user.save()
    return {"name": user.name}

@router.post("/init")
def init():
    user, create = User.get_or_create(
        name = "admin",
        defaults = {
            "password": hashlib.sha256("password".encode("utf-8")).hexdigest(),
            "email" : "email"
        }
    )
    if not create:
        user.password = hashlib.sha256("password".encode("utf-8")).hexdigest()
        user.save()
    return {"name": user.name}