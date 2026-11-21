from rest_framework.views import exception_handler
from uuid import uuid4
from rest_framework.response import Response
from typing import Any
from rest_framework import status
import logging

from projects.presentation.exceptions import (
    EXCEPTION_MAPPER as PROJECT_EXCEPTION_MAPPER,
)
from accounts.presentation.exceptions import (
    EXCEPTION_MAPPER as ACCOUNT_EXCEPTION_MAPPER,
)

ALL_EXCEPTION_MAPPER = PROJECT_EXCEPTION_MAPPER | ACCOUNT_EXCEPTION_MAPPER

LOGGER = logging.getLogger("exceptions")


def custom_exception_handler(exc: BaseException, context: Any) -> Response | None:

    response = exception_handler(exc, context)

    if response is not None:
        status_code = ALL_EXCEPTION_MAPPER.get(
            exc, default=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            error_id = uuid4()
            LOGGER.error(f"[{error_id}] Unhandled error occured: {exc}", exc_info=True)
            output = {
                "details": "Something went wrong. Please try again later",
                "error_id": error_id,
            }
        else:
            output = {"details": str(exc)}

        response.status_code = status_code
        response.data = output

    return response
