from typing import Any, List
from fastapi.responses import JSONResponse

def success_response(data: Any, message: str = "Success") -> dict:
    """Wrap success response in standard format"""
    if isinstance(data, list):
        return {"data": data, "message": message, "success": True}
    return {"data": data, "message": message, "success": True}

def error_response(message: str, errors: List[str] = None) -> dict:
    """Wrap error response in standard format"""
    response = {"message": message, "success": False}
    if errors:
        response["errors"] = errors
    return response

