from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using the configured password hasher."""

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify that a plain-text password matches a stored password hash."""

    return password_hasher.verify(
        plain_password,
        hashed_password,
    )
