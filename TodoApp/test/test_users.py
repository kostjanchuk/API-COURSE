from fastapi import status
from ..routers.users import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user_authenticated(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'admin'
    assert response.json()['email'] == 'admin@admin.com'
    assert response.json()['first_name'] == 'Kostya'
    assert response.json()['last_name'] == 'Yarosh'
    assert response.json()['role'] == 'admin'


def test_change_password_authenticated(test_user):
    response_data = {'password': 'admin',
                     'new_password': 'admin'}

    response = client.put('/user/password', json=response_data)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_authenticated_not_valid(test_user):
    response_data = {'password': 'wrong_password',
                     'new_password': 'admin'}

    response = client.put('/user/password', json=response_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not valid password'}
