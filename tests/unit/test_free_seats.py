from services.licensing.constants import INFINITE_INT
from services.licensing.utils import nof_free_seats


def test_nof_free_seats__ok():
    assert nof_free_seats(100, 10, 99) == 11
    assert nof_free_seats(100, 10, 100) == 10
    assert nof_free_seats(100, 10, 101) == 9
    assert nof_free_seats(100, 10, 110) == 0
    assert nof_free_seats(100, 10, 111) == 0

    assert nof_free_seats(-1, 10, 99) == INFINITE_INT
    assert nof_free_seats(-1, 10, 999) == INFINITE_INT
    assert nof_free_seats(-1, 10, 999999) == INFINITE_INT
    assert nof_free_seats(-1, 10, 9999999) == INFINITE_INT

    assert nof_free_seats(100, 0, 99) == 1
    assert nof_free_seats(100, 0, 100) == 0
    assert nof_free_seats(100, 0, 101) == 0
    assert nof_free_seats(100, 0, 110) == 0
    assert nof_free_seats(100, 0, 111) == 0

    assert nof_free_seats(-1, 0, 99) == INFINITE_INT
    assert nof_free_seats(-1, 0, 999) == INFINITE_INT
    assert nof_free_seats(-1, 0, 99999) == INFINITE_INT
    assert nof_free_seats(-1, 0, 9999999) == INFINITE_INT
