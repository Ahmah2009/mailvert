from email_validator import EmailNotValidError, validate_email


def check_syntax(address: str) -> tuple[bool, str | None, str | None]:
    """Validate RFC-compliant syntax and split into (local, domain).

    Returns (is_valid, normalized_local_part, domain). On failure the local
    part and domain are None.
    """
    try:
        result = validate_email(address, check_deliverability=False)
    except EmailNotValidError:
        return False, None, None
    return True, result.local_part, result.domain.lower()
