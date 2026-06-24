import bcrypt

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    # bcrypt requires bytes, so we encode the string
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Decode back to a string so it can be stored in PostgreSQL easily
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        # Failsafe in case the hash format is corrupted
        return False