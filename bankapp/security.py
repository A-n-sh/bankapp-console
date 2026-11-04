import hashlib
import hmac
import secrets

from bankapp.errors import ValidationError

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 200_000


def validate_pin(pin: str) -> None:
    if not (pin.isdigit() and 4 <= len(pin) <= 6):
        raise ValidationError("PIN must be 4 to 6 digits.")


def hash_pin(pin: str, *, iterations: int = _ITERATIONS) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, iterations)
    return f"{_ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def verify_pin(pin: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    if algorithm != _ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt_hex), int(iterations))
    return hmac.compare_digest(digest.hex(), digest_hex)
