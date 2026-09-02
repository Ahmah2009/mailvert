import asyncio

import typer
from rich.console import Console
from rich.table import Table

from mailvert.core.verifier import verify
from mailvert.models import Status

app = typer.Typer(help="mailvert — verify email address deliverability from the command line.")
console = Console()

_STATUS_STYLE = {
    Status.VALID: "green",
    Status.INVALID: "red",
    Status.RISKY: "yellow",
    Status.UNKNOWN: "grey58",
}


@app.command()
def verify_cmd(
    emails: list[str] = typer.Argument(..., help="One or more email addresses to verify"),  # noqa: B008
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the result cache"),
) -> None:
    """Verify one or more email addresses."""
    results = asyncio.run(_verify_all(emails, use_cache=not no_cache))

    table = Table(title="mailvert results")
    table.add_column("email")
    table.add_column("status")
    table.add_column("score")
    table.add_column("domain")
    table.add_column("catch-all")
    table.add_column("reasons")

    for result in results:
        style = _STATUS_STYLE[result.status]
        table.add_row(
            result.email,
            f"[{style}]{result.status.value}[/{style}]",
            f"{result.score:.2f}",
            result.domain or "-",
            "-" if result.catch_all is None else str(result.catch_all),
            "; ".join(result.reasons) or "-",
        )

    console.print(table)


async def _verify_all(emails: list[str], use_cache: bool) -> list:
    return await asyncio.gather(*(verify(e, use_cache=use_cache) for e in emails))


if __name__ == "__main__":
    app()
