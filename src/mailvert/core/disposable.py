"""Lightweight, dependency-free disposable-domain and role-account detection.

This is intentionally a small curated set rather than a bundled third-party
list — good enough to catch the common throwaway providers without shipping
and maintaining a large static dataset. Swap in an external feed if you need
exhaustive coverage.
"""

DISPOSABLE_DOMAINS: frozenset[str] = frozenset(
    {
        "mailinator.com",
        "guerrillamail.com",
        "10minutemail.com",
        "tempmail.com",
        "temp-mail.org",
        "yopmail.com",
        "trashmail.com",
        "getnada.com",
        "throwawaymail.com",
        "fakeinbox.com",
        "sharklasers.com",
        "dispostable.com",
    }
)

ROLE_LOCAL_PARTS: frozenset[str] = frozenset(
    {
        "admin",
        "administrator",
        "support",
        "info",
        "sales",
        "contact",
        "help",
        "billing",
        "noreply",
        "no-reply",
        "postmaster",
        "webmaster",
        "abuse",
    }
)


def is_disposable(domain: str) -> bool:
    return domain.lower() in DISPOSABLE_DOMAINS


def is_role_account(local_part: str) -> bool:
    return local_part.lower() in ROLE_LOCAL_PARTS
