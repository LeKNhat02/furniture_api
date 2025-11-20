from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle pydantic validation errors"""
    errors = exc.errors()
    formatted_errors = []
    
    for error in errors:
        formatted_errors.append({
            "loc": list(error["loc"]),
            "msg": error["msg"],
            "type": error["type"]
        })
    
    logger.error(f"Validation error on {request.url.path}: {formatted_errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": formatted_errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )

def register_error_handlers(app: FastAPI):
    """Register custom error handlers"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
