from mailvert.core import cache, smtp_check
from mailvert.core.disposable import is_disposable, is_role_account
from mailvert.core.dns_lookup import get_mx_hosts
from mailvert.core.syntax import check_syntax
from mailvert.exceptions import DomainResolutionError
from mailvert.logging import get_logger
from mailvert.models import Status, VerificationResult

log = get_logger("verifier")


def _score(status: Status, smtp_deliverable: bool | None, catch_all: bool | None) -> float:
    if status is Status.INVALID:
        return 0.0
    if status is Status.VALID:
        return 1.0 if not catch_all else 0.75
    if status is Status.RISKY:
        return 0.4
    return 0.5  # unknown


async def verify(email: str, use_cache: bool = True) -> VerificationResult:
    email = email.strip()

    if use_cache:
        cached = cache.get(email)
        if cached is not None:
            return cached

    syntax_valid, local_part, domain = check_syntax(email)
    if not syntax_valid:
        result = VerificationResult(
            email=email,
            status=Status.INVALID,
            score=0.0,
            syntax_valid=False,
            reasons=["invalid email syntax"],
        )
        if use_cache:
            cache.set(email, result)
        return result

    assert domain is not None and local_part is not None
    disposable = is_disposable(domain)
    role_account = is_role_account(local_part)

    reasons: list[str] = []
    if disposable:
        reasons.append("disposable/throwaway domain")
    if role_account:
        reasons.append("role-based mailbox (not a personal address)")

    try:
        mx_hosts = await get_mx_hosts(domain)
    except DomainResolutionError as exc:
        result = VerificationResult(
            email=email,
            status=Status.INVALID,
            score=0.0,
            syntax_valid=True,
            domain=domain,
            disposable=disposable,
            role_account=role_account,
            reasons=[*reasons, str(exc)],
        )
        if use_cache:
            cache.set(email, result)
        return result

    smtp_result = await smtp_check.probe(mx_hosts, email, domain)
    reasons.append(smtp_result.detail)

    if smtp_result.deliverable is True:
        status = Status.VALID
    elif smtp_result.deliverable is False:
        status = Status.INVALID
    else:
        status = Status.RISKY if disposable or role_account else Status.UNKNOWN

    result = VerificationResult(
        email=email,
        status=status,
        score=_score(status, smtp_result.deliverable, smtp_result.catch_all),
        syntax_valid=True,
        domain=domain,
        mx_records=mx_hosts,
        disposable=disposable,
        role_account=role_account,
        catch_all=smtp_result.catch_all,
        smtp_deliverable=smtp_result.deliverable,
        reasons=reasons,
    )
    if use_cache:
        cache.set(email, result)
    return result
