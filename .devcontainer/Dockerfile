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
    PI_OFFLINE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl git openssh-client htop ripgrep fd-find make procps less nano \
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

COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
    && pip install --no-compile --only-binary=:all: -r /tmp/requirements.txt \
    && pip check \
    && rm /tmp/requirements.txt \
    && mkdir -p /root/.pi/agent /workspace \
    && printf 'export PATH=/opt/venv/bin:$PATH\n' > /etc/profile.d/python-venv.sh

COPY --chmod=755 pi.py /usr/local/bin/pi
USER root
WORKDIR /workspace
CMD ["sleep", "infinity"]
