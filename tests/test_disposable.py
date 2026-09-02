from mailvert.core.disposable import is_disposable, is_role_account


def test_known_disposable_domain():
    assert is_disposable("mailinator.com") is True


def test_normal_domain_not_disposable():
    assert is_disposable("gmail.com") is False


def test_role_account_detected():
    assert is_role_account("support") is True
    assert is_role_account("jane.doe") is False
