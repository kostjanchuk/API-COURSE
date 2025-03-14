from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Path, Query, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from .auth import get_current_user
from starlette.responses import RedirectResponse
from .. import models
from ..database import SessionLocal

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="TodoApp/templates")

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "title",
                "description": "description",
                "priority": 3,
                "complete": 0,
            }
        }
    }


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


# Pages

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {'request': request, 'todos': todos, 'user': user})

    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {'request': request, 'user': user})
    except:
        return redirect_to_login()


@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {'request': request, 'user': user, "todo": todo})
    except:
        return redirect_to_login()


# Endpoints
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authenticate failed')

    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()


@router.get('/todo/{todos_id}', status_code=status.HTTP_200_OK)
async def read_todos_by_id(user: user_dependency, db: db_dependency, todos_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authenticate failed')

    todo_model = db.query(models.Todos).filter(models.Todos.id == todos_id).filter(
        models.Todos.owner_id == user.get('id')).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')


# @router.get('/todo', status_code=status.HTTP_200_OK)
# async def read_todos_by_priority(user: user_dependency, db: db_dependency, todos_priority: int = Query(gt=0, lt=6)):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authenticate failed')
#
#     todo_model = db.query(models.Todos).filter(models.Todos.priority == todos_priority).filter(
#         models.Todos.owner_id == user.get('id')).all()
#
#     if todo_model is not None:
#         return todo_model
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def crete_todo(db: db_dependency, user: user_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')

    todo_model = models.Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority

    db.add(todo_model)
    db.commit()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
