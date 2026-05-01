"""
BuildCore Security Utilities.

JWT token creation/verification with Argon2 password hashing
and secure invite-token generation.
"""

import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.config import get_settings
from app.core.exceptions import UnauthorizedError

settings = get_settings()

# Argon2 hasher with OWASP-recommended defaults
_phasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    """Create a short-lived access JWT.

    Args:
        data: Payload claims (must include "sub" for user id).

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh JWT.

    Args:
        data: Payload claims (must include "sub" for user id).

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Decode and verify a JWT.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        UnauthorizedError: If token is expired, malformed, or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise UnauthorizedError(
            message="Invalid or expired token",
            details={"reason": str(exc)},
        ) from exc


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def get_password_hash(password: str) -> str:
    """Hash a plaintext password using Argon2id.

    Args:
        password: Plain-text password.

    Returns:
        Argon2 hash string.
    """
    return _phasher.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against an Argon2 hash.

    Args:
        plain: Plain-text password.
        hashed: Stored Argon2 hash.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return _phasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ---------------------------------------------------------------------------
# Invite token
# ---------------------------------------------------------------------------

def generate_invite_token() -> str:
    """Generate a cryptographically secure invite token.

    Returns:
        36-character URL-safe random string.
    """
    return secrets.token_urlsafe(27)  # 27 bytes → 36 base64url chars
