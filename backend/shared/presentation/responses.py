"""Helpers shared by the API views of every app.

Every error response has a "details" string; field errors go to "errors".
"""

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response

INVALID_REQUEST_DETAILS = "Invalid request data."
UNEXPECTED_ERROR_DETAILS = "Something went wrong. Please try again later."


def error_response(
    details: str, status_code: int, errors: dict[str, Any] | None = None
) -> Response:
    body: dict[str, Any] = {"details": details}
    if errors:
        body["errors"] = errors
    return Response(body, status=status_code)


def unexpected_error_response(logger: logging.Logger, context: str) -> Response:
    """Log the traceback and hide the internal details from the client.

    Has to be called inside an "except" block, so the full traceback lands in
    the logs.
    """
    logger.exception("Unexpected error in %s", context)
    return error_response(
        UNEXPECTED_ERROR_DETAILS, status.HTTP_500_INTERNAL_SERVER_ERROR
    )
