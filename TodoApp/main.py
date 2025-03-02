from fastapi import FastAPI, Depends, Path, Query
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import models

from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    Complete: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "title",
                "description": "description",
                "priority": 3,
                "Complete": 0,
            }
        }
    }


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(models.Todos).all()


@app.get('/todos/{todos_id}', status_code=status.HTTP_200_OK)
async def read_todos_by_id(db: db_dependency, todos_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todos_id).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Item not found')


@app.get('/todos/', status_code=status.HTTP_200_OK)
async def read_todos_by_priority(db: db_dependency, todos_priority: int = Query(gt=0, lt=6)):
    return db.query(models.Todos).filter(models.Todos.priority == todos_priority).all()


@app.post('/todos/create_todo', status_code=status.HTTP_201_CREATED)
async def crete_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = models.Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()


@app.put('/todos/update_todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Item not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.Complete = todo_request.Complete
    todo_model.priority = todo_request.priority

    db.add(todo_model)
    db.commit()


@app.delete('/todos/delete_todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
