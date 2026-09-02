import time
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    RISKY = "risky"
    UNKNOWN = "unknown"


class VerificationResult(BaseModel):
    email: str
    status: Status
    score: float = Field(ge=0.0, le=1.0, description="Confidence the address is deliverable")

    syntax_valid: bool
    domain: str | None = None
    mx_records: list[str] = Field(default_factory=list)

    disposable: bool = False
    role_account: bool = False
    catch_all: bool | None = None
    smtp_deliverable: bool | None = None

    reasons: list[str] = Field(default_factory=list)
    cached: bool = False
    checked_at: float = Field(default_factory=time.time)


class BulkVerificationRequest(BaseModel):
    emails: list[str]


class BulkVerificationResult(BaseModel):
    results: list[VerificationResult]
