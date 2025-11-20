from typing import Union
from fastapi import HTTPException, status

def validate_id(id_value: Union[str, int]) -> int:
    """
    Validate and convert ID to integer.
    Raises HTTPException if conversion fails.
    """
    try:
        return int(id_value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {id_value}. ID must be an integer."
        )

def validate_positive_int(value: int, field_name: str = "value") -> int:
    """
    Validate that integer is positive (> 0).
    """
    if value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be greater than 0"
        )
    return value

def validate_non_negative_int(value: int, field_name: str = "value") -> int:
    """
    Validate that integer is non-negative (>= 0).
    """
    if value < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be greater than or equal to 0"
        )
    return value
