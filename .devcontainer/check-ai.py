"""Keep Codex login state usable across container restarts and rebuilds."""
import os
from pathlib import Path
import re
import tomllib

codex = Path(os.environ["CODEX_HOME"])
codex.mkdir(parents=True, exist_ok=True)
# Codex recreates its daemon socket; an old link points into a previous container's /tmp.
socket = codex / "app-server-control" / "app-server-control.sock"
if socket.is_symlink() and not socket.exists():
    socket.unlink()
# Store credentials as a file in the volume, not in a keyring that dies with the container.
config = codex / "config.toml"
original = config.read_text() if config.exists() else ""
if tomllib.loads(original).get("cli_auth_credentials_store") != "file":
    head, sep, tables = original.partition("\n[")
    head = re.sub(r"(?m)^\s*cli_auth_credentials_store\s*=.*\n?", "", head)
    config.write_text('cli_auth_credentials_store = "file"\n' + head + sep + tables)
