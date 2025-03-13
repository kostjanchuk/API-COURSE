from fastapi import status
from ..routers.admin import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_todos_authenticated(test_todo):
    response = client.get('/admin')
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()) == 1


def test_delete_todo_by_id_authenticated(test_todo):
    response = client.delete('/admin/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()

    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None


def test_delete_todo_by_id_authenticated_not_found(test_todo):
    response = client.delete('/admin/999')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}
