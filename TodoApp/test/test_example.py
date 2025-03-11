import pytest


class Worker:

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


def test_gt():
    assert 7 > 4


def test_isinstance():
    assert isinstance('string', str)
    assert isinstance(1234, int)
    assert not isinstance((), set)


def test_type():
    assert type('string' is str)
    assert type('124' is not int)


def test_list():
    lst = [1, 2, 3, 4, 5, 6, 7]
    empty_lst = []

    assert 1 in lst
    assert all(lst)
    assert not any(empty_lst)


@pytest.fixture
def default_employee():
    return Worker('Steve', 'Jobs')


def test_person_initialization(default_employee):
    assert default_employee.first_name == 'Steve'
    assert default_employee.last_name == 'Jobs'



