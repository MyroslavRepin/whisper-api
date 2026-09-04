"""Central error handling: turn framework errors into short, human messages."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

# Human names for request fields, used when reporting validation errors.
FIELD_LABELS = {
    "audio_file": "Audio file",
    "email": "Email",
}


def _field_label(location: tuple) -> str:
    # loc looks like ("body", "email"); the last element is the field name.
    name = str(location[-1]) if location else "request"
    return FIELD_LABELS.get(name, name.replace("_", " ").capitalize())


def _humanize(error: dict) -> str:
    label = _field_label(tuple(error.get("loc", ())))
    error_type = error.get("type", "")

    if error_type == "missing":
        return f"{label} is required"
    if error_type.startswith("value_error"):
        reason = (error.get("ctx") or {}).get("reason") or error.get("msg", "")
        return f"{label} is invalid: {reason}" if reason else f"{label} is invalid"
    return f"{label}: {error.get('msg', 'invalid value')}"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.warning(f"Validation failed for {request.url.path}: {errors}")
        # Single string detail: the frontend can show it as-is.
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "; ".join(_humanize(error) for error in errors)
                or "Invalid request",
                "errors": jsonable_encoder(errors),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.opt(exception=exc).error(f"Unhandled error on {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Server error. The request did not go through."},
        )
