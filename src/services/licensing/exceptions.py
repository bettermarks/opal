from typing import Any, Optional, Dict
from fastapi import HTTPException as FastApiHTTPException


class HTTPException(FastApiHTTPException):
    def __init__(
        self,
        status_code: int,
        message: Any = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> None:
        self.kwargs = kwargs
        self.message = message
        super().__init__(status_code=status_code, detail=message, headers=headers)


class DuplicateEntryException(Exception):
    pass
