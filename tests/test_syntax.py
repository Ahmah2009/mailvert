from mailvert.core.syntax import check_syntax


def test_valid_address():
    ok, local, domain = check_syntax("Jane.Doe@Example.com")
    assert ok is True
    assert local == "Jane.Doe"
    assert domain == "example.com"


def test_missing_at_sign():
    ok, local, domain = check_syntax("not-an-email")
    assert ok is False
    assert local is None
    assert domain is None


def test_missing_domain():
    ok, _, _ = check_syntax("user@")
    assert ok is False
