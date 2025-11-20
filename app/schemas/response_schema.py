from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar('T')


class DataResponse(BaseModel, Generic[T]):
    """Generic response wrapper for API responses."""
    data: T
    message: Optional[str] = None
    status_code: int = 200

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "message": "Success",
                "status_code": 200
            }
        }


class ListDataResponse(BaseModel):
    """Response wrapper for list of items."""
    data: List = []
    message: Optional[str] = None
    status_code: int = 200

    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "message": "Success",
                "status_code": 200
            }
        }
