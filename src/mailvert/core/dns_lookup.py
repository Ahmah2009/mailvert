import dns.asyncresolver
import dns.exception
import dns.resolver

from mailvert.config import settings
from mailvert.exceptions import DomainResolutionError
from mailvert.logging import get_logger

log = get_logger("dns")


async def get_mx_hosts(domain: str) -> list[str]:
    """Return mail-exchanger hostnames for a domain, ordered by preference.

    Falls back to the domain's own A/AAAA record per RFC 5321 §5.1 when no
    MX record is published. Raises DomainResolutionError if the domain does
    not exist or nothing accepts mail for it.
    """
    resolver = dns.asyncresolver.Resolver()
    resolver.timeout = settings.dns_timeout_seconds
    resolver.lifetime = settings.dns_timeout_seconds

    try:
        answer = await resolver.resolve(domain, "MX")
        hosts = [str(r.exchange).rstrip(".") for r in sorted(answer, key=lambda r: r.preference)]
        if hosts:
            return hosts
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN as exc:
        raise DomainResolutionError(f"domain does not exist: {domain}") from exc
    except dns.exception.Timeout as exc:
        raise DomainResolutionError(f"DNS lookup timed out for: {domain}") from exc
    except dns.exception.DNSException as exc:
        raise DomainResolutionError(f"DNS lookup failed for {domain}: {exc}") from exc

    # No MX record — fall back to the bare domain if it at least resolves.
    try:
        await resolver.resolve(domain, "A")
        return [domain]
    except dns.exception.DNSException as exc:
        raise DomainResolutionError(f"no MX or A record for domain: {domain}") from exc
