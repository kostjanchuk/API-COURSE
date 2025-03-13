from datetime import timedelta
import pytest

from starlette.exceptions import HTTPException
from jose import jwt
from starlette import status

from ..routers.auth import get_db, get_current_user, bcrypt_context, authenticate_user, SECRET_KEY, ALGORITHM, \
    create_access_token
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'admin', db)

    assert authenticated_user is not None

    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('WrongUsername', 'admin', db)

    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'adminwrong', db)

    assert wrong_password_user is False


def test_create_access_token():
    username = 'admin'
    user_id = 1
    role = 'admin'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'admin', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token)
    assert user == {'username': 'admin', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user'
