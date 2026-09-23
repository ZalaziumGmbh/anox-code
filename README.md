# anox-code

Baue deine erste App mit Python, HTML und KI – unter Windows.

## 1. Einmal vorbereiten

1. [VS Code](https://code.visualstudio.com/download) installieren.
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installieren, starten und während der Arbeit laufen lassen. Falls verlangt, den PC neu starten.
3. In VS Code unter **Erweiterungen** nach **Dev Containers** von Microsoft suchen und installieren.

## 2. Projekt öffnen

1. **[Projekt herunterladen](https://github.com/ZalaziumGmbh/anox-code/archive/refs/heads/main.zip)** → Rechtsklick auf die ZIP → **Alle extrahieren …**.
2. In VS Code über **Datei → Ordner öffnen …** den Ordner mit **README.md** und **src** öffnen.
3. **F1** drücken → **Dev Containers: Reopen in Container** wählen.

Warte, bis unten links **Dev Container: anox-code** steht und alle Erweiterungen
installiert sind. Das dauert beim ersten Mal einige Minuten.

## 3. KI-Schlüssel eintragen

Öffne die automatisch angelegte Datei **`.env`** und trage den API-Schlüssel deiner IT ein:

```dotenv
key=DEIN_API_SCHLUESSEL
```

Mit **Strg+S** speichern. Schon eingetragen? Weiter zu Schritt 4.
Gib den Schlüssel nicht weiter.

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
