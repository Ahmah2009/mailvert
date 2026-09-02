import asyncio

from fastapi import APIRouter, HTTPException, Query

from mailvert.config import settings
from mailvert.core.verifier import verify
from mailvert.models import BulkVerificationRequest, BulkVerificationResult, VerificationResult

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/v1/verify", response_model=VerificationResult)
async def verify_single(email: str = Query(..., description="Email address to verify")) -> VerificationResult:
    return await verify(email)


@router.post("/v1/verify/bulk", response_model=BulkVerificationResult)
async def verify_bulk(payload: BulkVerificationRequest) -> BulkVerificationResult:
    if len(payload.emails) > settings.bulk_max_addresses:
        raise HTTPException(
            status_code=422,
            detail=f"at most {settings.bulk_max_addresses} addresses per request",
        )

    semaphore = asyncio.Semaphore(settings.bulk_concurrency)

    async def bounded_verify(address: str) -> VerificationResult:
        async with semaphore:
            return await verify(address)

    results = await asyncio.gather(*(bounded_verify(addr) for addr in payload.emails))
    return BulkVerificationResult(results=list(results))
