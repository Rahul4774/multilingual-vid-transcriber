from pydantic import Field
from typing import TypedDict, Optional

class ErrorState(TypedDict):
    error: Optional[str] = None
    status: int = Field(..., description="Error status code")
    message: str = Field(..., description="Error message")