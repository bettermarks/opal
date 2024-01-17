from services.licensing.constants import INFINITE_INT


def nof_free_seats(nof_seats: int, extra_seats: int, seats_occupied: int) -> int:
    """
    returns the number of free seats of a license using some encoding for
    'invinite' number of free seats.
    :param nof_seats: number of seats attached to the license (-1 ='infinite')
    :param extra_seats: optional 'extra seats' (0 for no extra seats)
    :param seats_occupied: number of already occupied seats
    :return: the number of still free (unoccupied) seats for the license.
    If nof_seats has the encoded infinity value (-1), the function returns
    INFINITE_INT (currently represented by 1E18 as an integer)!
    """
    if nof_seats is None or extra_seats is None or extra_seats < 0:
        raise ValueError("Illegal value for 'nof_seats' or 'extra_seats'")
    if nof_seats < 0:
        return INFINITE_INT
    return max(nof_seats + extra_seats - seats_occupied, 0)
