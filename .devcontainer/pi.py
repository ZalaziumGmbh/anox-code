#!/opt/venv/bin/python
"""Load the workspace's .env as data, configure Pi, then replace this process."""

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

# Defaults maintained centrally in GitHub. Only the key is required in .env.
LLM_MODEL = "azure-gpt-5.6-luna"
LLM_URL = "https://prd.billing.zalazium.de"
MODEL_ALIAS = "anox-code"


def configure():
    env_file = Path("/workspace/.env")
    # Exclusive creation never overwrites an existing file, even during parallel starts.
    try:
        descriptor = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write("key=\n")
    if not env_file.is_file():
        raise OSError(".env muss eine Datei sein.")
    values = dotenv_values(env_file, encoding="utf-8-sig", interpolate=False)

    def setting(name, default=""):
        return (
            (values.get(name) or "").strip()
            or (values.get(name.upper()) or "").strip()
            or default
        )

    key = setting("key")
    if not key or key == "DEIN_API_SCHLUESSEL":
        return False

    model = setting("llm", LLM_MODEL)
    base_url = setting("url", LLM_URL).rstrip("/").removesuffix("/chat/completions")
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Die optionale URL muss eine HTTPS-Basis-URL sein.")
    if not base_url.endswith("/v1"):
        base_url += "/v1"

    os.environ["LITELLM_API_KEY"] = key
    agent_dir = Path.home() / ".pi" / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.environ["PI_CODING_AGENT_DIR"] = str(agent_dir)
    models = {
        "providers": {
            "litellm": {
                "baseUrl": base_url,
                "api": "openai-completions",
                "apiKey": "$LITELLM_API_KEY",
                "compat": {
                    "supportsStore": False,
                    "supportsDeveloperRole": False,
                    "maxTokensField": "max_completion_tokens",
                },
                # Pi displays the id, not the name. Keep the API model separate.
                "models": [{"id": MODEL_ALIAS, "samplingParams": {"model": model}}],
            }
        }
    }
    settings_file = agent_dir / "settings.json"
    settings = json.loads(settings_file.read_text()) if settings_file.exists() else {}
    if not isinstance(settings, dict):
        raise TypeError("settings.json muss ein JSON-Objekt enthalten.")
    settings.update(
        defaultProvider="litellm",
        defaultModel=MODEL_ALIAS,
        enableInstallTelemetry=False,
        enableAnalytics=False,
        cacheWarming="off",
    )
    # Atomic replacement also handles two terminals starting Pi together.
    for name, data in (("models.json", models), ("settings.json", settings)):
        target = agent_dir / name
        temporary = target.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(target)
    return True


def main():
    # Help/version remain usable even before credentials are configured.
    if sys.argv[1:] not in (["--help"], ["-h"], ["--version"], ["-v"]):
        try:
            ready = configure()
        except (OSError, TypeError, ValueError):
            # Never include exception details: they may contain .env values.
            print(
                "Pi konnte nicht eingerichtet werden. "
                "Trage in .env deinen API Schluessel als key=... ein und speichere. "
                "Falls du eine eigene url eingetragen hast, pruefe auch deren HTTPS-Adresse. "
                "Falls der Fehler bleibt, wende dich an die IT.",
                file=sys.stderr,
            )
            return 1
        if not ready:
            print(
                "Oeffne .env in VS Code, fuege deinen API Schluessel hinter key= ein "
                "und speichere. Danach im Terminal pi eingeben."
            )
            # The container can finish setup before the customer enters a key.
            return 0 if sys.argv[1:] == ["--setup"] else 1
    if sys.argv[1:] == ["--setup"]:
        print("Pi ist eingerichtet. Im Terminal einfach pi eingeben.")
        return 0
    os.execv("/opt/pi/pi", ["/opt/pi/pi", *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
