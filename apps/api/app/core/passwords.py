"""Common password blacklist check (OWASP recommendation)."""

# Top 100 most common passwords — a minimal set for Phase 1.
# Phase 2+: load full 10k list from file.
COMMON_PASSWORDS = frozenset(
    {
        "password",
        "123456",
        "12345678",
        "qwerty",
        "abc123",
        "monkey",
        "1234567",
        "letmein",
        "trustno1",
        "dragon",
        "baseball",
        "iloveyou",
        "master",
        "sunshine",
        "ashley",
        "michael",
        "shadow",
        "123123",
        "654321",
        "superman",
        "qazwsx",
        "football",
        "password1",
        "password123",
        "welcome",
        "welcome1",
        "admin",
        "admin123",
        "login",
        "princess",
        "starwars",
        "passw0rd",
        "hello",
        "charlie",
        "donald",
        "qwerty123",
        "mustang",
        "access",
        "flower",
        "hottie",
        "loveme",
        "zaq1zaq1",
        "666666",
        "888888",
        "111111",
        "000000",
        "121212",
        "1q2w3e4r",
        "1qaz2wsx",
        "qwertyuiop",
    }
)


def is_common_password(password: str) -> bool:
    """Check if password is in the common passwords blacklist."""
    return password.lower() in COMMON_PASSWORDS
