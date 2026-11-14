import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("uvicorn.error")


def register_error_handlers(app: FastAPI):
    """
    Global exception handlers:
    - Known client errors (HTTPException) return their exact status and message.
    - Validation errors (RequestValidationError) return clean field error lists.
    - ANY unexpected exception, database crash, or unhandled bug is caught globally
      and returns a standardized 500 Internal Server Error.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.detail,
                "errors": None
            },
            headers=getattr(exc, "headers", None)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for err in exc.errors():
            loc = err.get("loc", [])
            field = ".".join(str(l) for l in loc if l != "body") or "payload"
            formatted_errors.append({
                "field": field,
                "message": err.get("msg", "Invalid value")
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error: Please check your input fields.",
                "errors": formatted_errors
            }
        )

    @app.exception_handler(Exception)
    async def global_internal_server_error_handler(request: Request, exc: Exception):
        # Log the full exception traceback on the server console for debugging
        logger.exception(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}")

        # Return clean 500 Internal Server Error to the client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error. Please try again later.",
                "errors": None
            }
        )
