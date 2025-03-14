from fastapi import FastAPI, Request
from starlette import status

from .routers import auth, todos, admin, users
from fastapi.responses import RedirectResponse
from . import models
from fastapi.staticfiles import StaticFiles
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")


@app.get('/')
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@app.get('/healthy', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status': 'healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
