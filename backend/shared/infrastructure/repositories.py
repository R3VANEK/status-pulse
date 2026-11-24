import functools
from typing import Callable, Any
from abc import ABCMeta


class RepositoryException(Exception):
    """Base repository exception class."""


class TooManyRecordsReturnedException(RepositoryException):
    """Raised when query returned unexpectedly too many records"""


class RepositoryExceptionWrapper(ABCMeta):
    """metaclass for all repositories that guarantees any exception from within their methods is RepositoryException"""

    @staticmethod
    def exception_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable[..., Any]:
            try:
                return func(*args, **kwargs)
            except RepositoryException as e:
                raise e
            except BaseException as e:
                raise RepositoryException from e

        wrapper.__isabstractmethod__ = getattr(func, "__isabstractmethod__", False)  # type: ignore
        return wrapper

    def __new__(cls, name, bases, namespace):

        for attr_name, attr in namespace.items():
            if isinstance(attr, staticmethod):
                namespace[attr_name] = staticmethod(
                    RepositoryExceptionWrapper.exception_wrapper(attr.__func__)
                )

            elif isinstance(attr, classmethod):
                namespace[attr_name] = classmethod(
                    RepositoryExceptionWrapper.exception_wrapper(attr.__func__)
                )

            elif callable(attr):
                namespace[attr_name] = RepositoryExceptionWrapper.exception_wrapper(
                    attr
                )

        return super().__new__(cls, name, bases, namespace)
