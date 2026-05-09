# auth.py — Password Hashing & Verification Module
# Uses passlib with the bcrypt scheme — the industry-standard algorithm
# for securely hashing passwords before database storage.

from passlib.context import CryptContext

# CryptContext configuration:
#   schemes=['bcrypt']   — use bcrypt as the hashing algorithm
#   deprecated='auto'   — automatically flag old/weak hashes for rehashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    """
    Hash a plaintext password and return the bcrypt hash string.

    Called during user creation / seeding (/seed-users route).
    The resulting hash is stored in the users.password_hash column.
    The plaintext password is NEVER stored or logged.

    Example:
        hash_password('password123')
        → '$2b$12$LJ3m4ys...'  (60-character bcrypt hash)
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a submitted plaintext password against the stored bcrypt hash.

    Called during login (POST /login route).
    Returns True if the password matches, False otherwise.

    Security note: bcrypt internally handles the salt — no manual
    salt management is required.

    Example:
        verify_password('password123', '$2b$12$LJ3m4ys...')
        → True
    """
    return pwd_context.verify(plain, hashed)
