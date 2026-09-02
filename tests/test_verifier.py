import pytest

from mailvert.core import smtp_check
from mailvert.core.verifier import verify
from mailvert.exceptions import DomainResolutionError
from mailvert.models import Status


@pytest.mark.asyncio
async def test_invalid_syntax_short_circuits(mocker):
    mx_mock = mocker.patch("mailvert.core.verifier.get_mx_hosts")
    result = await verify("not-an-email")
    assert result.status is Status.INVALID
    assert result.syntax_valid is False
    mx_mock.assert_not_called()


@pytest.mark.asyncio
async def test_unresolvable_domain_is_invalid(mocker):
    mocker.patch(
        "mailvert.core.verifier.get_mx_hosts",
        side_effect=DomainResolutionError("domain does not exist: nonexistent-domain-xyz.com"),
    )
    result = await verify("user@nonexistent-domain-xyz.com")
    assert result.status is Status.INVALID
    assert result.syntax_valid is True


@pytest.mark.asyncio
async def test_deliverable_mailbox_is_valid(mocker):
    mocker.patch("mailvert.core.verifier.get_mx_hosts", return_value=["mx1.example.com"])
    mocker.patch(
        "mailvert.core.verifier.smtp_check.probe",
        return_value=smtp_check.SmtpProbeResult(True, True, False, "SMTP 250"),
    )
    result = await verify("user@example.com")
    assert result.status is Status.VALID
    assert result.score == 1.0
    assert result.mx_records == ["mx1.example.com"]


@pytest.mark.asyncio
async def test_rejected_mailbox_is_invalid(mocker):
    mocker.patch("mailvert.core.verifier.get_mx_hosts", return_value=["mx1.example.com"])
    mocker.patch(
        "mailvert.core.verifier.smtp_check.probe",
        return_value=smtp_check.SmtpProbeResult(True, False, None, "SMTP 550"),
    )
    result = await verify("nobody@example.com")
    assert result.status is Status.INVALID
    assert result.score == 0.0


@pytest.mark.asyncio
async def test_catch_all_domain_lowers_confidence(mocker):
    mocker.patch("mailvert.core.verifier.get_mx_hosts", return_value=["mx1.example.com"])
    mocker.patch(
        "mailvert.core.verifier.smtp_check.probe",
        return_value=smtp_check.SmtpProbeResult(True, True, True, "SMTP 250"),
    )
    result = await verify("anyone@example.com")
    assert result.status is Status.VALID
    assert result.catch_all is True
    assert result.score == 0.75


@pytest.mark.asyncio
async def test_result_is_cached(mocker):
    get_mx = mocker.patch("mailvert.core.verifier.get_mx_hosts", return_value=["mx1.example.com"])
    mocker.patch(
        "mailvert.core.verifier.smtp_check.probe",
        return_value=smtp_check.SmtpProbeResult(True, True, False, "SMTP 250"),
    )
    first = await verify("user@example.com")
    second = await verify("user@example.com")
    assert first.cached is False
    assert second.cached is True
    get_mx.assert_called_once()
