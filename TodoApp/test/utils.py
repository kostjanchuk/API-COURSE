from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..database import Base
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from ..routers.auth import bcrypt_context

import pytest

from ..models import Todos, User

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'admin', 'id': 1, 'role': 'admin'}


@pytest.fixture
def test_todo():
    todo = Todos(
        title='todo 1',
        description='test todo',
        priority='5',
        complete=False,
        owner_id=1

    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = User(
        email='admin@admin.com',
        username='admin',
        first_name='Kostya',
        last_name='Yarosh',
        hashed_password=bcrypt_context.hash('admin'),
        role='admin'

    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
