from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, message: str, detail: str | None = None) -> None:
        super().__init__(status_code=status_code, detail={"message": message, "detail": detail})
        self.message = message
        self.error_detail = detail


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(status.HTTP_409_CONFLICT, message)


class BadRequestError(AppError):
    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, message, detail)


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)
