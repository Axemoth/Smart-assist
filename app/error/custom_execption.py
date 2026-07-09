from typing import Any, Callable, Awaitable
from fastapi.requests import Request
from fastapi.responses import JSONResponse


# Base class
class TodoAppExecption(Exception):
    """This is the base class for whole application errors"""

    ...


# Rate Limit Error
class RateLimit(TodoAppExecption):
    """User has reached limit of api calling in given period"""

    ...


# Token Error
class InvalidToken(TodoAppExecption):
    """User has provided an invalid or expired token"""

    ...


# Admin Error
class AdminNotAuthenticated(TodoAppExecption):
    """User not logged in as admin"""

    ...


# User Error
class UserNotFound(TodoAppExecption):
    """User not found"""

    ...


class UserNotAuthenticated(TodoAppExecption):
    """User is not logged in"""

    ...


class UserAlreadyExists(TodoAppExecption):
    """User has provided and email for a user who exists during sign up"""

    ...


class InvalidCredentials(TodoAppExecption):
    """User has provided wrong email or password during log in"""

    ...


class UserNotVerified(TodoAppExecption):
    """User has not completed verification process"""

    ...


# Task Error
class TaskNotFound(TodoAppExecption):
    """Task not found"""

    ...


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:

    async def exception_handler(request: Request, exc: Exception):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def create_global_handler(status_code: int, initial_detail: dict) -> Callable:
    """Factory to create the global handler exception"""

    async def custom_handler(req: Request, exc: Exception):

        error_type = type(exc).__name__
        error_msg = str(exc) if str(exc) else f"Internal {error_type} occurred"

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": initial_detail.get("message", "Internal Server Error"),
                "error_code": error_type,
                "technical_details": error_msg,
            },
        )

    return custom_handler
