from fastapi import status
from ..routers.todos import get_db, get_current_user
from .utils import *
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all_authenticated(test_todo):
    response = client.get('/todos')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'todo 1',
                                'description': 'test todo',
                                'owner_id': 1,
                                'priority': 5,
                                'complete': False,
                                'id': 1
                                }]


def test_get_one_authenticated(test_todo):
    response = client.get('/todos/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'todo 1',
                               'description': 'test todo',
                               'owner_id': 1,
                               'priority': 5,
                               'complete': False,
                               'id': 1
                               }


def test_get_one_authenticated_not_found():
    response = client.get('/todos/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}


def test_create_todo_authenticated(test_todo):
    response_data = {'title': 'todo 2',
                     'description': 'test todo 2',
                     'priority': 5,
                     'complete': False,
                     }

    response = client.post('todos/todo', json=response_data)

    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()

    todo_model = db.query(Todos).filter(Todos.id == 2).first()

    assert response_data.get('description') == todo_model.description
    assert response_data.get('priority') == todo_model.priority
    assert response_data.get('complete') == todo_model.complete
    assert response_data.get('title') == todo_model.title


def test_update_todo_authenticated(test_todo):
    response_data = {'title': 'todo 1 update',
                     'description': 'test todo update',
                     'priority': 5,
                     'complete': False,
                     }

    response = client.put('todos/todo/1', json=response_data)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()

    todo_model = db.query(Todos).filter(Todos.id == 1).first()

    assert response_data.get('description') == todo_model.description
    assert response_data.get('priority') == todo_model.priority
    assert response_data.get('complete') == todo_model.complete
    assert response_data.get('title') == todo_model.title


def test_update_todo_authenticated_not_found(test_todo):
    response_data = {'title': 'todo 1 update',
                     'description': 'test todo update',
                     'priority': 5,
                     'complete': False,
                     }

    response = client.put('todos/todo/999', json=response_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}


def test_delete_todo_authenticated(test_todo):
    response = client.delete('todos/todo/1')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None


def test_delete_todo_authenticated_not_found(test_todo):
    response = client.delete('todos/todo/999')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Item not found'}
