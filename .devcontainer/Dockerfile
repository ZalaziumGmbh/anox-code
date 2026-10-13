# syntax=docker/dockerfile:1
FROM python:3.14-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    LANG=C.UTF-8 \
    EDITOR=nano \
    PI_OFFLINE=1 \
    CODEX_HOME=/persist/codex \
    CLAUDE_CONFIG_DIR=/persist/claude \
    PI_CODING_AGENT_DIR=/persist/pi/agent \
    DISABLE_AUTOUPDATER=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl git openssh-client htop ripgrep fd-find make procps less nano \
       libatomic1 libstdc++6 \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd \
    && git config --system --add safe.directory /workspace \
    && rm -rf /var/lib/apt/lists/*

# Official standalone release: no Node/npm needed. Pin version AND checksums.
RUN set -eu; \
    case "$(dpkg --print-architecture)" in \
      amd64) arch=x64; sha=2494f5587a8774a10296d00a7e504e7ad05596ca93e057cb89372c8b1a7f46a9 ;; \
      arm64) arch=arm64; sha=3957cb7ac3ec84fe905f0f077c599fd3fecfbb886a93467dfebfacc108b8c3b7 ;; \
      *) echo 'Supported architectures: amd64, arm64' >&2; exit 1 ;; \
    esac; \
    curl --fail --show-error --silent --location --retry 3 \
      --proto '=https' --tlsv1.2 \
      "https://github.com/earendil-works/pi/releases/download/v0.86.1/pi-linux-${arch}.tar.gz" \
      -o /tmp/pi.tar.gz; \
    echo "$sha  /tmp/pi.tar.gz" | sha256sum --check -; \
    mkdir -p /opt/pi; \
    tar -xzf /tmp/pi.tar.gz -C /opt/pi --strip-components=1; \
    rm /tmp/pi.tar.gz; \
    /opt/pi/pi --version

# Native Codex and Claude CLIs, pinned; built in a throwaway HOME without credentials.
ARG CODEX_VERSION=0.162.1
ARG CLAUDE_VERSION=2.1.287
RUN set -eu; \
    stage=$(mktemp -d); \
    curl -fsSL --retry 3 https://chatgpt.com/codex/install.sh -o "$stage/codex.sh"; \
    curl -fsSL --retry 3 https://claude.ai/install.sh -o "$stage/claude.sh"; \
    env -i HOME="$stage" PATH=/usr/local/bin:/usr/bin:/bin CODEX_NON_INTERACTIVE=1 \
      sh "$stage/codex.sh" --release "$CODEX_VERSION"; \
    env -i HOME="$stage" PATH=/usr/local/bin:/usr/bin:/bin \
      bash "$stage/claude.sh" "$CLAUDE_VERSION"; \
    mkdir -p /opt/zalazium-ai; \
    cp -a "$(readlink -f "$stage/.codex/packages/standalone/current")" /opt/zalazium-ai/codex; \
    if [ -x /opt/zalazium-ai/codex/bin/codex ]; then codex=/opt/zalazium-ai/codex/bin/codex; \
    else codex=/opt/zalazium-ai/codex/codex; fi; \
    ln -s "$codex" /usr/local/bin/codex; \
    install -m 0755 "$(readlink -f "$stage/.local/bin/claude")" /opt/zalazium-ai/claude; \
    ln -s /opt/zalazium-ai/claude /usr/local/bin/claude; \
    rm -rf "$stage"; \
    test "$(codex --version)" = "codex-cli $CODEX_VERSION"; \
    claude --version | grep -F "$CLAUDE_VERSION" >/dev/null

COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
    && pip install --no-compile --only-binary=:all: -r /tmp/requirements.txt \
    && pip check \
    && rm /tmp/requirements.txt \
    && install -d -m 0700 -o root -g root /persist /persist/codex /persist/claude /persist/pi /persist/pi/agent \
    && mkdir -p /workspace \
    && printf 'export PATH=/opt/venv/bin:$PATH\n' > /etc/profile.d/python-venv.sh

COPY --chmod=755 pi.py /usr/local/bin/pi
USER root
WORKDIR /workspace
CMD ["sleep", "infinity"]
