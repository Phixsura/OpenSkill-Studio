"""R551: production-compose env drill — the whack-a-mole ender.

Renders docker-compose.prod.yml with placeholder secrets and imports the
app settings under EXACTLY each backend service's environment. Every
production boot validator (JWT/S3/encryption-key/domain-verifier/CORS/DB
creds) runs — a service whose env drifts from what production boot
requires fails HERE, not at 2am. (Found dead-on-arrival: migrate with only
DATABASE_URL (R550); DOMAIN_VERIFIER missing on all three (R551);
CREDENTIAL_ENCRYPTION_KEY never plumbed (R549).)

Usage: uv run python tests/drills/compose_env_drill.py   (from apps/api)
"""

import json
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
API = os.path.join(REPO, "apps/api")


def main() -> int:
    key = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-c",
            "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())",
        ],
        capture_output=True,
        text=True,
        cwd=API,
        timeout=120,
    ).stdout.strip()
    render_env = {
        **os.environ,
        "DB_PASSWORD": "drill-pass",
        "JWT_SECRET": "drill-unique-jwt-secret-123456",
        "CREDENTIAL_ENCRYPTION_KEY": key,
        "S3_ACCESS_KEY": "drill-access",
        "S3_SECRET_KEY": "drill-secret",
    }
    cfg = json.loads(
        subprocess.run(
            ["docker", "compose", "-f", "docker-compose.prod.yml", "config", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=REPO,
            env=render_env,
            timeout=120,
        ).stdout
    )
    failed = 0
    for svc in ("api", "worker", "migrate"):
        env = {
            k: str(v)
            for k, v in (cfg["services"][svc].get("environment") or {}).items()
            if v is not None
        }
        env.setdefault("APP_ENV", "production")  # Dockerfile ENV
        env["PATH"] = os.environ["PATH"]
        r = subprocess.run(
            ["uv", "run", "python", "-c", "from app.config import settings; print('OK')"],
            capture_output=True,
            text=True,
            env=env,
            cwd=API,
            timeout=120,
        )
        if r.returncode == 0:
            print(f"  ok   {svc}: production settings import clean")
        else:
            failed += 1
            errs = re.findall(r"^([a-z_]+)\n\s+Value error, ([^\[]+)", r.stderr, re.M)
            print(f"  FAIL {svc}: {errs or r.stderr.strip().splitlines()[-1][:160]}")
    print("DRILL OK" if not failed else f"DRILL FAILED ({failed})")
    return 0 if not failed else 1


sys.exit(main())
