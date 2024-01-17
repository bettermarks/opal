"""
(From ChatGPT): The unit of work pattern is a design pattern used to manage
transactions in software applications that interact with a database. The
basic idea behind the pattern is to group a set of related database operations
into a single "unit of work" that can be executed as a single transaction.

This file implements the 'unit of work' pattern in an abstract
class "TransactionManager". Concrete implementations of that interface
could use for example
- PostgreSQL and
- SqlAlchemy

The implementation of this unit of work class is taken from
    José Haro Peralta, Microservice APIs, Manning Publications,
    2023, ISBN: 9781617298417
"""
from abc import ABC, abstractmethod


class TransactionManager(ABC):
    @abstractmethod
    def __init__(self, implicit_commit: bool = False):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, traceback):
        pass

    @property
    @abstractmethod
    def session(self):
        pass

    @property
    @abstractmethod
    def engine(self):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
