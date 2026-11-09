#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'BOOTSTRAP'
from pathlib import Path
import base64
import json
import os
import re
import secrets

root = Path.cwd()
for directory in ["data/raw", "data/interim", "data/processed", "reports/figures",
                  "runtime/mlflow/artifacts", "runtime/airflow/logs", "runtime/airflow/auth",
                  "runtime/jupyter", "runtime/api/model-cache"]:
    (root / directory).mkdir(parents=True, exist_ok=True)
# PostgreSQL's entrypoint initializes and owns its private directory.
(root / "runtime/postgres").mkdir(parents=True, exist_ok=True)
env = root / ".env"
if not env.exists():
    template = (root / ".env.example").read_text()
    template = re.sub(r"CHANGE_ME_[A-Z_]+", lambda _: secrets.token_hex(24), template)
    template = re.sub(r"^AIRFLOW_FERNET_KEY=.*$", "AIRFLOW_FERNET_KEY=" +
                      base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(), template, flags=re.M)
    template = re.sub(r"^LOCAL_UID=.*$", f"LOCAL_UID={os.getuid()}", template, flags=re.M)
    template = re.sub(r"^LOCAL_GID=.*$", f"LOCAL_GID={os.getgid()}", template, flags=re.M)
    env.write_text(template)
    env.chmod(0o600)
    print("Created .env with generated local secrets.")
else:
    print("Preserved existing .env.")
values = dict(line.split("=", 1) for line in env.read_text().splitlines()
              if line and not line.startswith("#") and "=" in line)
required = dict(line.split("=", 1) for line in (root / ".env.example").read_text().splitlines()
                if line and not line.startswith("#") and "=" in line)
missing = set(required) - values.keys()
if missing or "CHANGE_ME_" in env.read_text():
    raise SystemExit("Existing .env has missing values/placeholders. Compare with .env.example.")
auth = root / "runtime/airflow/auth/passwords.json"
if not auth.exists():
    auth.write_text(json.dumps({values["AIRFLOW_ADMIN_USER"]: values["AIRFLOW_ADMIN_PASSWORD"]}) + "\n")
    auth.chmod(0o600)
# Airflow uses the host UID with group 0; the owner can write host-mounted files.
print("Bind-mount directories ready. Existing data and credentials preserved.")
BOOTSTRAP
