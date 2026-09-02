# mailvert

Async email address verification: syntax, MX resolution, live SMTP
deliverability, catch-all and disposable/role-account detection — as an
HTTP API, a CLI, and a Python library.

This is a from-scratch rebuild of a 2016 single-file Python 2 Flask script
that did one thing (a blocking `RCPT TO` handshake). The verification idea
is the same one described in the [Background](#background) section below;
everything else — structure, async I/O, caching, tests, packaging — is new.

## Features

- **Layered verification pipeline**: syntax → disposable/role check → MX
  lookup → live SMTP `RCPT TO` probe → catch-all detection, short-circuiting
  as soon as a stage proves the address invalid.
- **Async end-to-end**: FastAPI + `dnspython`'s async resolver; the blocking
  SMTP handshake runs in a worker thread via `asyncio.to_thread` so it never
  stalls the event loop.
- **Bulk verification** with bounded concurrency (`POST /api/v1/verify/bulk`).
- **Result caching** (TTL) so repeat lookups of the same address skip the
  network round trip.
- **Rate limiting** (`slowapi`) and structured (optionally JSON) logging.
- **CLI** (`mailvert user@example.com`) with a Rich table.
- **Typed** end to end (Pydantic models, `mypy`-checked).
- Fully unit tested with DNS/SMTP mocked — no network access needed to run
  the test suite.

## Quickstart

```bash
pip install -e ".[dev]"
cp .env.example .env   # adjust SMTP identity, timeouts, etc.
make run                # http://localhost:8000/docs for interactive OpenAPI docs
```

```bash
curl "http://localhost:8000/api/v1/verify?email=someone@example.com"
```

```json
{
  "email": "someone@example.com",
  "status": "valid",
  "score": 1.0,
  "syntax_valid": true,
  "domain": "example.com",
  "mx_records": ["mx1.example.com"],
  "disposable": false,
  "role_account": false,
  "catch_all": false,
  "smtp_deliverable": true,
  "reasons": ["SMTP 250"],
  "cached": false
}
```

### CLI

```bash
mailvert someone@example.com another@company.com
```

### Docker

```bash
docker compose up --build
```

## Why results can be `unknown`

Many mail servers greylist or accept-then-bounce unfamiliar senders, and a
large share of cloud hosts block outbound port 25 entirely. When the SMTP
probe can't get a clean accept/reject, or is disabled
(`MAILVERT_SMTP_PROBE_ENABLED=false`), mailvert reports `unknown` rather
than guessing — verification degrades gracefully to syntax + MX-only
checking instead of producing false confidence.

## Project layout

```
src/mailvert/
  config.py          settings (env-driven, MAILVERT_* prefix)
  models.py           Pydantic request/response models
  core/
    syntax.py          RFC syntax validation
    disposable.py       disposable-domain / role-account heuristics
    dns_lookup.py       async MX (+A fallback) resolution
    smtp_check.py       SMTP RCPT TO probe + catch-all detection
    cache.py            TTL result cache
    verifier.py          orchestrates the pipeline above
  api/
    app.py               FastAPI app factory, middleware, rate limiting
    routes.py             /api/v1/verify, /api/v1/verify/bulk, /api/healthz
  cli.py                 Typer CLI
tests/                    pytest suite, DNS/SMTP mocked via pytest-mock
```

## Background

The underlying deliverability check is the same manual trick you can run
by hand:

1. Find the domain's mail exchanger:
   `dig example.com mx`
2. Connect to it on port 25:
   `telnet mail.example.com 25`
3. Introduce yourself: `HELO local.domain.name`
4. Declare a sender: `MAIL FROM: mail@domain.ext`
5. Ask about the recipient: `RCPT TO: mail@otherdomain.ext`
6. Read the response code (`250`/`251` accept, `550`/`551`/`553` reject).

mailvert automates that sequence, adds the checks that make it trustworthy
in practice (syntax validation, disposable/role detection, catch-all
detection so a domain that accepts *everything* doesn't read as "valid"),
and wraps it in an API/CLI that doesn't block on every request.

## Development

```bash
make install   # editable install + dev deps
make test
make lint
```

## License

MIT
