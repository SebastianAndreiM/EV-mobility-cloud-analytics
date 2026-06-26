"""Domain exceptions mapped to HTTP responses by handlers in main.py."""


class AppError(Exception):
    status_code = 400
    detail = "Application error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class UnauthorizedError(AppError):
    status_code = 401
    detail = "Not authenticated"


class ConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class RateLimitError(AppError):
    status_code = 429
    detail = "Rate limit exceeded"


class ModelNotTrainedError(AppError):
    status_code = 409
    detail = "Model has not been trained yet"
