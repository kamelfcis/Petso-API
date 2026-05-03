"""Optional password hashers (see `PASSWORD_HASHERS` in settings)."""

from django.contrib.auth.hashers import PBKDF2PasswordHasher


class PetsoDemoPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    """
    Faster PBKDF2 for demo / graduation servers where signup latency matters.

    Enable only with env `PETSO_FAST_PASSWORD_HASHING=1`.
    Do not use for real production accounts facing internet attacks.
    """

    iterations = 120_000
