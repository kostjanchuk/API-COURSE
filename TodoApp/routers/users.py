from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session
from starlette import status
from ..models import Todos, User

from ..database import SessionLocal
from starlette.exceptions import HTTPException

from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class RequestVerification(BaseModel):
    password: str
    new_password: str


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='authenticate failed')

    return db.query(User).filter(User.id == user.get('id')).first()


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: RequestVerification):
    if user is None:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='authenticate failed')

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not valid password')

    user_model.hashed_password = bcrypt_context.hash(user_verification.password)

    db.add(user_model)
    db.commit()
