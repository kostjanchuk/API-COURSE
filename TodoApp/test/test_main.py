from .utils import *
from fastapi import status


def test_return_health_check():
    response = client.get('/healthy')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'healthy'}
