# Native AI tools for anox-code

Choose **anox-code (developer)** when VS Code asks for a container profile.
The developer profile lives at `developer/devcontainer.json`; its SSH mounts and
container name are unchanged.
An existing workspace must select this profile before rebuilding; use
**Dev Containers: Switch Container** if VS Code remembers a previous selection.
Do not choose the customer profile to recover a missing native login.

The development image installs Codex 0.162.1 and Claude 2.1.287 with the official
curl installers. Binaries live under `/opt/zalazium-ai`; the feature applies only to development builds.
Restart checks do not download installers or inspect authentication files.

## State volume

All tool state lives in one private, root-owned volume `anox-code-volume`, mounted at
`/persist`; the development user is root. `CODEX_HOME=/persist/codex`,
`CLAUDE_CONFIG_DIR=/persist/claude` (including `.claude.json`) and
`PI_CODING_AGENT_DIR=/persist/pi/agent`. Docker fills a new volume from the image's
private skeleton; no host variables or manual volume creation are needed. The name
survives rebuilds, branch switches and folder renames.
Codex keeps its self-updating app-server daemon under `/persist/codex/packages/`.
`check-ai.py` refuses a missing, foreign-owned or group/other-readable `/persist`.

The main container is `anox-code`. A simultaneous checkout sets
`ZALAZIUM_DEV_SUFFIX=-<name>`, which selects both a separate container name and
volume `anox-code-<name>-volume`; Docker refuses an occupied name instead of replacing it.
Do not have two CLI sessions write the same state concurrently.

The customer profile mounts `anox-code-customer-volume` at `/persist` and keeps only
Pi state in `/persist/pi/agent`. Customer hosts need no migration: `pi --setup`
regenerates that state from `.env` when the container is created.

## Migration from separate volumes

Older developer setups used the host variables `ANOX_CODE_CODEX_VOLUME`,
`ANOX_CODE_CLAUDE_VOLUME` and `ANOX_CODE_PI_VOLUME` at `/root/.codex`, `/root/.claude`
and `/root/.pi`. Migrate them on the Docker host, outside any devcontainer, with
Mastermind's `scripts/devcontainer_volume.py`: without arguments it lists
devcontainers; `<old-container> anox-code-volume` previews and `--apply` stops the
container and copies the state without printing contents. It skips Codex packages and
daemon runtime records, keeps newer target state, refuses conflicts and leaves the old
volumes untouched. Pi state can also be regenerated with `pi --setup`. Then rebuild,
verify the CLIs without re-login, and keep the old volumes until a separately approved
deletion. Do not commit or upload login state.

## Synthetic qualification

Run `.devcontainer/qualify.py` only as an isolated unprivileged tester on a clean
source copy with a rootless Docker daemon and `@devcontainers/cli` 0.89.0 on PATH.
Pass only the tester HOME/PATH, XDG_RUNTIME_DIR and DOCKER_HOST environment.
The checker refuses a runtime `.env`, creates an empty synthetic one, and selects a
new labelled state volume through `ZALAZIUM_DEV_SUFFIX` without using developer
authentication. It qualifies the developer profile only; the customer profile has no
native CLIs and is not covered. It exercises the private root-owned `/persist`
(including the Pi directory), native CLI versions, initial setup, stop/start and
container recreation, refusal of a conflicting checkout, and folder rename with
a persistent synthetic marker. It restores the public
configuration and removes only its own containers and labelled volumes.
Current full build/lifecycle coverage is Linux amd64; another platform needs its
own qualification. A synthetic marker does not establish real login persistence.
