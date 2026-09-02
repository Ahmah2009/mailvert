import asyncio
import smtplib
import uuid
from dataclasses import dataclass

from mailvert.config import settings
from mailvert.logging import get_logger

log = get_logger("smtp")

_DELIVERABLE_CODES = {250, 251}
_UNDELIVERABLE_CODES = {550, 551, 553}


@dataclass
class SmtpProbeResult:
    performed: bool
    deliverable: bool | None
    catch_all: bool | None
    detail: str


def _probe_sync(mx_host: str, mailbox: str, domain: str, probe_catch_all: bool) -> SmtpProbeResult:
    """Blocking SMTP handshake, run off the event loop via a thread.

    Sequence mirrors a manual `telnet mx 25` deliverability check:
    connect -> EHLO/HELO -> MAIL FROM -> RCPT TO -> QUIT.
    """
    try:
        with smtplib.SMTP(timeout=settings.smtp_timeout_seconds) as client:
            client.connect(mx_host, 25)
            client.ehlo_or_helo_if_needed()
            client.mail(settings.smtp_from_address)

            code, _ = client.rcpt(mailbox)
            deliverable = code in _DELIVERABLE_CODES
            if code not in _DELIVERABLE_CODES and code not in _UNDELIVERABLE_CODES:
                # Greylisted / ambiguous response — treat as unknown, not a hard fail.
                deliverable = None

            catch_all: bool | None = None
            if probe_catch_all and deliverable:
                probe_address = f"{uuid.uuid4().hex}@{domain}"
                probe_code, _ = client.rcpt(probe_address)
                catch_all = probe_code in _DELIVERABLE_CODES

            return SmtpProbeResult(True, deliverable, catch_all, f"SMTP {code}")
    except (smtplib.SMTPException, OSError) as exc:
        return SmtpProbeResult(False, None, None, f"SMTP probe failed: {exc}")


async def probe(mx_hosts: list[str], mailbox: str, domain: str, probe_catch_all: bool = True) -> SmtpProbeResult:
    if not settings.smtp_probe_enabled:
        return SmtpProbeResult(False, None, None, "SMTP probing disabled")

    last_result = SmtpProbeResult(False, None, None, "no MX hosts to try")
    for mx_host in mx_hosts[: settings.max_mx_hosts_tried]:
        last_result = await asyncio.to_thread(_probe_sync, mx_host, mailbox, domain, probe_catch_all)
        if last_result.performed:
            return last_result
        log.debug("mx host %s unreachable, trying next", mx_host)
    return last_result
