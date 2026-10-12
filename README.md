# anox-code

Baue deine erste App mit Python, HTML und KI – unter Windows.

## 1. Einmal vorbereiten

1. [VS Code](https://code.visualstudio.com/download) installieren.
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installieren, starten und während der Arbeit laufen lassen. Falls verlangt, den PC neu starten.
3. In VS Code unter **Erweiterungen** nach **Dev Containers** von Microsoft suchen und installieren.

## 2. Projekt öffnen

1. **[Projekt herunterladen](https://github.com/ZalaziumGmbh/anox-code/archive/refs/heads/main.zip)** → Rechtsklick auf die ZIP → **Alle extrahieren …**.
2. In VS Code über **Datei → Ordner öffnen …** den Ordner mit **README.md** und **src** öffnen.
3. Press **F1** → **Dev Containers: Reopen in Container** → select **anox-code (customer)**.
   This profile needs no SSH key or volume configuration.
   Existing developer installations: select **anox-code (developer)** and follow
   [the state-preservation instructions](.devcontainer/AI-STATE.md) before rebuilding.

Warte, bis unten links **Dev Container: anox-code (customer)** steht und alle Erweiterungen
installiert sind. Das dauert beim ersten Mal einige Minuten.

## 3. KI-Schlüssel eintragen

Öffne die automatisch angelegte Datei **`.env`** und trage den API-Schlüssel deiner IT ein:

```dotenv
key=DEIN_API_SCHLUESSEL
```

Mit **Strg+S** speichern. Schon eingetragen? Weiter zu Schritt 4.
Gib den Schlüssel nicht weiter.

The default endpoint is `https://litellm.zalazium.de/v1`. Existing coding keys
remain valid. Known `https://prd.billing.zalazium.de` URLs are mapped to this
endpoint without rewriting `.env`; custom proxy URLs remain unchanged.

## 4. App starten

Drücke **F5** (bei Nachfrage **start** wählen). Die Beispiel-App öffnet sich im Browser.
Falls nicht: In VS Code unter **Ports** auf das Globus-Symbol klicken.

**Shift+F5** stoppt die App.

## 5. Mit der KI weiterbauen

Öffne **Terminal → Neues Terminal**, tippe `pi` ein und drücke **Enter**.
Schreibe zum Beispiel: „Ergänze ein Feld für die Telefonnummer.“ Danach die Webseite neu laden.

**Beenden:** `/exit` · **Unterhaltung fortsetzen:** `pi -c`

## Budget prüfen

Gib im VS-Code-Terminal ein:

```sh
make budget
```

## Später weiterarbeiten

Docker starten → Projektordner in VS Code öffnen → bei Bedarf
**F1 → Dev Containers: Reopen in Container** → **F5** für die App, `pi -c` im Terminal für die KI.

**Probleme?** Docker, API-Schlüssel und Firmen-VPN prüfen oder die IT fragen.

## Development container

Read [native CLI state and rebuild instructions](.devcontainer/AI-STATE.md) before
the first rebuild. All Codex/Claude/Pi state lives in the private volume
`anox-code-volume` at `/persist`; migrate older separate volumes first.
Native CLI binaries are installed in the development image, outside login state.
The shared CLI additions are confined to development-container builds.
