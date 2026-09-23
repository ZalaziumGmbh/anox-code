#!/opt/venv/bin/python
"""Load .env as data to start Pi or report the shared LiteLLM key budget."""

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import dotenv_values

# Defaults maintained centrally in GitHub. Only the key is required in .env.
LLM_MODEL = "anox-code"
LLM_URL = "https://prd.billing.zalazium.de"
MODEL_ALIAS = "anox-code"
ENV_FILE = Path("/workspace/.env")


def load_settings():
    if not ENV_FILE.is_file():
        raise OSError(".env muss eine Datei sein.")
    values = dotenv_values(ENV_FILE, encoding="utf-8-sig", interpolate=False)

    def setting(name, default=""):
        return (
            (values.get(name) or "").strip()
            or (values.get(name.upper()) or "").strip()
            or default
        )

    key = setting("key")
    if not key or key == "DEIN_API_SCHLUESSEL":
        return "", "", ""

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
    return key, model, base_url


def configure():
    # Exclusive creation never overwrites an existing file, even during parallel starts.
    try:
        descriptor = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write("key=\n")
    key, model, base_url = load_settings()
    if not key:
        return False

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


def budget_summary(info):
    """Report only the key's own cap; missing data must never look unlimited."""
    if not isinstance(info, dict) or not {"spend", "max_budget"} <= info.keys():
        raise ValueError("Budgetdaten fehlen.")
    spend, limit = info["spend"], info["max_budget"]
    for value in (spend,) if limit is None else (spend, limit):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Ungueltige Budgetdaten.")

    if limit is None:
        summary = "Coding-Budget: kein eigenes Limit gesetzt"
    else:
        percent = max(0, limit - spend) / limit * 100 if limit else 0
        summary = f"{percent:.1f} % coding budget verbleibend"
    if info.get("blocked"):
        summary += " (API-Schluessel gesperrt)"
    return summary


def show_budget():
    try:
        key, _, base_url = load_settings()
        if not key:
            print(
                "Budget: Bitte in .env deinen API-Schluessel als key=... eintragen.",
                file=sys.stderr,
            )
            return 1
    except (OSError, TypeError, ValueError):
        print(
            "Budget: Bitte key und die optionale HTTPS-url in .env pruefen.",
            file=sys.stderr,
        )
        return 1

    try:
        # Only the hash goes in the URL; the secret stays in the auth header.
        # Keep any proxy path prefix when removing the OpenAI-compatible /v1.
        response = httpx.get(
            base_url.removesuffix("/v1") + "/key/info",
            params={"key": hashlib.sha256(key.encode()).hexdigest()},
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
            follow_redirects=False,
        )
        if response.status_code == 403:
            message = (
                "Budget nicht abrufbar (HTTP 403). "
                "Die IT muss /key/info fuer diesen API-Schluessel freigeben."
            )
        elif response.status_code == 401:
            message = "Budget: API-Schluessel abgelehnt (HTTP 401). Bitte .env pruefen."
        elif response.status_code != 200:
            message = f"Budget nicht abrufbar (HTTP {response.status_code})."
        else:
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Ungueltige Antwort.")
            print(budget_summary(payload.get("info")))
            return 0
    except httpx.RequestError:
        message = "Budget: LiteLLM nicht erreichbar. Verbindung und Firmen-VPN pruefen."
    except httpx.InvalidURL:
        message = "Budget: Bitte die optionale HTTPS-url in .env pruefen."
    except (TypeError, ValueError, OverflowError):
        message = "Budget: LiteLLM hat keine gueltigen Budgetdaten geliefert."
    # Never print response bodies or exception details: they may contain secrets.
    print(message, file=sys.stderr)
    return 1


def main():
    if sys.argv[1:] == ["--budget"]:
        return show_budget()
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
