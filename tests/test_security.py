import pytest

from bankapp.errors import ValidationError
from bankapp.security import hash_pin, validate_pin, verify_pin


def test_hash_and_verify():
    stored = hash_pin("1234", iterations=1000)
    assert "1234" not in stored
    assert verify_pin("1234", stored)
    assert not verify_pin("4321", stored)
    assert hash_pin("1234", iterations=1000) != stored  # salted


def test_verify_rejects_garbage():
    assert not verify_pin("1234", "not-a-hash")


@pytest.mark.parametrize("pin", ["123", "1234567", "12a4", ""])
def test_validate_pin_rejects(pin):
    with pytest.raises(ValidationError):
        validate_pin(pin)
