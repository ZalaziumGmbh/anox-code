# anox-code

Deine erste Anwendung mit Python, HTML und KI. Anleitung für Windows.

## 1. Einmal vorbereiten

- [VS Code](https://code.visualstudio.com/download) installieren und öffnen.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installieren und starten. Falls verlangt, den Rechner neu starten. Docker während der Arbeit laufen lassen.
- In VS Code die Erweiterung [Dev Containers von Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installieren (**Erweiterungen → Dev Containers suchen → Installieren**).

## 2. Projekt öffnen

1. **[Projekt als ZIP herunterladen](https://github.com/ZalaziumGmbh/anox-code/archive/refs/heads/main.zip)** und per Rechtsklick → **Alle extrahieren …** entpacken.
2. In VS Code **Datei → Ordner öffnen …** wählen. Den entpackten Ordner öffnen, in dem **README.md** und **src** liegen.
3. **F1** drücken → **Dev Containers: Reopen in Container** wählen.

Warte, bis unten links **Dev Container: anox-code** steht und die Erweiterungen
installiert sind. Beim ersten Mal dauert das einige Minuten.

## 3. KI-Schlüssel eintragen

Öffne in VS Code die automatisch angelegte Datei **`.env`** und trage deinen
API-Schlüssel von der IT ein:

```dotenv
key=DEIN_API_SCHLUESSEL
```

Mit **Strg+S** speichern. Ist der Schlüssel schon eingetragen, gehe weiter.
Gib die Datei und den Schlüssel niemals weiter.

## 4. App starten

Drücke **F5** und wähle bei Bedarf **start**. Im Browser öffnet sich **Mein Servicetag**,
eine Aufgaben-App mit Beispieltickets. Deine Aufgaben bleiben im Browser gespeichert.
Öffnet sich kein Browser, klicke in VS Code unter **Ports** auf das Globus-Symbol.

Mit **Shift+F5** stoppst du die App, mit **F5** startest du sie erneut.

## 5. Mit der KI weiterbauen

Wähle in VS Code **Terminal → Neues Terminal**, tippe `pi` ein und drücke **Enter**.
Schreibe zum Beispiel: „Ergänze ein Feld für die Telefonnummer.“
Nach Änderungen speichern und die Webseite neu laden.

Mit `/exit` beendest du die KI, mit `pi -c` setzt du die Unterhaltung später fort.

## Später weiterarbeiten

Docker Desktop starten → denselben Projektordner in VS Code öffnen → bei Bedarf
**F1 → Dev Containers: Reopen in Container** → **F5** für die App oder `pi` im Terminal für die KI.

Bei Problemen: Docker Desktop, Schlüssel und Firmen-VPN prüfen oder deine IT fragen.