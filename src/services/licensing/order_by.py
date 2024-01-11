from typing import List, Tuple

from fastapi import status as http_status

from services.licensing.exceptions import HTTPException
from services.licensing.custom_types import OrderByDirection


def get_order_by_fields(
    encoded_order_by_clause: str, allowed_fields: List[str]
) -> List[Tuple[str, OrderByDirection]]:
    """
    helper: parses an order by clause (given as a string), performs some checks
    and returns a list of order by fields together with their 'order direction'.
    For example, an order by clause
        -id.product_eid.-manager_eid
    would result in
    [
        "id", OrderByDirection.DESC,
        "product_eid", OrderByDirection.ASC
        "manager_ied", OrderByDirection.DESC
    ]

    :param encoded_order_by_clause:
    :param allowed_fields:
    :return (see example above)
    :raises an HTTPException on not expected order by field
    """
    if not encoded_order_by_clause:
        return []
    fields = [
        (f[1:], OrderByDirection.DESC) if f[0] == "-" else (f, OrderByDirection.ASC)
        for f in encoded_order_by_clause.split(".")
    ]
    for f in fields:
        if f[0] not in allowed_fields:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                message="Order by parameter contains an unsupported field",
                field=f[0],
                allowed_fields=allowed_fields,
            )
    return fields
