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

    mapped_status = ALL_EXCEPTION_MAPPER.get(
        type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    if response is None:
        if mapped_status == status.HTTP_500_INTERNAL_SERVER_ERROR:
            error_id = uuid4()
            LOGGER.error(
                "[%s] Unhandled error occured: %s", error_id, exc, exc_info=True
            )
            return Response(
                {
                    "details": "Something went wrong. Please try again later",
                    "error_id": str(error_id),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        else:
            return Response(status=mapped_status, data={"details": str(exc)})

    return response
