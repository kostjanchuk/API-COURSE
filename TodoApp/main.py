from fastapi import FastAPI
from starlette import status

from .routers import auth, todos, admin, users

from . import models

from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get('/healthy', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status': 'healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
