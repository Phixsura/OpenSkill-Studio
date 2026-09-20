# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email security@openskill.studio with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive a response within 48 hours

## Supported Versions

| Version | Supported |
|---------|-----------|
| main    | ✅        |

## Security Measures

- All API endpoints require authentication (except public career pages and credential verification)
- Passwords are hashed with bcrypt (72-byte truncation enforced)
- JWT tokens with configurable expiry
- CORS with explicit origin allowlist
- Rate limiting on all talent API endpoints
- Input validation via Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via React auto-escaping + html.escape in server renders
- SSRF protection on webhook URLs (private IP rejection)
- Cookie security flags (httpOnly, secure, sameSite)
- Content Security Policy headers
