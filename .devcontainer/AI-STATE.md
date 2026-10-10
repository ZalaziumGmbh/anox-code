# Native AI tools for anox-code

The development image installs Codex 0.162.1 and Claude 2.1.287 with the official
curl installers. Binaries live under `/opt/zalazium-ai`; the feature applies only to development builds.
Restart checks do not download installers or inspect authentication files.

Before the first rebuild, inspect the previous container's mount names, targets
and owner with `docker inspect --format '{{json .Mounts}}' <old-container>`.
Do not display login files. Keep the old container and volumes until acceptance.
Set these host environment variables before launching your editor:

```sh
export ANOX_CODE_CODEX_VOLUME='<your-existing-codex-volume>'
export ANOX_CODE_CLAUDE_VOLUME='<your-existing-claude-volume>'
```

For a new workspace use stable developer-specific names, for example
`anox-code-alice-codex` and `anox-code-alice-claude`. Never share a login volume
between founders. Explicitly create both volumes with `docker volume create`
only for a new login; initialization checks volume metadata and refuses missing
selections before a container can replace the old one. Branch switches and repository renames must keep these names.
If authentication exists only in the previous container's writable layer, copy it
locally into the chosen volumes before rebuilding; preserve the separate
`~/.claude.json` as `.claude/.claude.json`. Do not commit or upload either cache.
The previous state must remain available until a real login survives a rebuild.

The main container is `anox-code`. A simultaneous checkout may set
`ZALAZIUM_DEV_SUFFIX=-prd`; Docker refuses an occupied name instead of replacing it.
Use separate state volumes for simultaneously running checkouts; do not have two
CLI sessions write the same state concurrently. The development user remains root.
Verify both CLIs, log in personally, restart and rebuild, then verify the same
login still works. Synthetic state tests do not prove provider authentication.

Previous state mount declarations (choose their actual existing volume IDs):

- `source=${devcontainerId}-pi,target=/root/.pi,type=volume`

Also set `ANOX_CODE_PI_VOLUME` to the existing Pi volume before rebuilding.

## Synthetic qualification

Run `.devcontainer/qualify.py` only as an isolated unprivileged tester on a clean
source copy with a rootless Docker daemon and `@devcontainers/cli` 0.89.0 on PATH.
Pass only the tester HOME/PATH, XDG_RUNTIME_DIR and DOCKER_HOST environment.
The checker refuses a runtime `.env`, creates an empty synthetic one, and selects
new labelled state volumes without using developer authentication. It exercises
missing-volume refusal, native CLI versions, initial setup, stop/start and
container recreation, refusal of a conflicting checkout, and folder rename with
a persistent synthetic marker. It restores the public
configuration and removes only its own containers and labelled volumes.
For nonroot development users, the rootless test copies the clean source into a
disposable workspace volume to preserve user ownership without changing host files.
Current full build/lifecycle coverage is Linux amd64; another platform needs its
own qualification. A synthetic marker does not establish real login persistence.
