class MailvertError(Exception):
    """Base class for all mailvert errors."""


class InvalidSyntaxError(MailvertError):
    """The address is not a syntactically valid email address."""


class DomainResolutionError(MailvertError):
    """No usable MX (or fallback A) record could be found for the domain."""
