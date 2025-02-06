from pydantic import BaseModel # type: ignore
from typing import Optional

class VerificationResponse(BaseModel):
    success: bool
    message: str
    match_found: Optional[bool] = None
    confidence: Optional[float] = None

class VerificationResult(BaseModel):
    is_match: bool
    confidence: float 