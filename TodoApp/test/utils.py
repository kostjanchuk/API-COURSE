from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from ..main import app
from ..database import Base
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

import pytest

from ..models import Todos

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
    return {'username': 'testadmin', 'id': 1, 'user_role': 'admin'}


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
