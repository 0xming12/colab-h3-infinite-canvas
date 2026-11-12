#!/bin/bash
# Install the official Colab CLI in this repository, without touching system Python.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v uv >/dev/null 2>&1; then
    echo "需要先安装 uv：https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi
uv venv --python 3.13 "$ROOT/.venv"
uv pip install --python "$ROOT/.venv/bin/python" 'google-colab-cli==0.8.0'
"$ROOT/.venv/bin/colab" version
echo "Colab CLI 已安装。账号授权请由账号持有人在终端运行：$ROOT/.venv/bin/colab sessions"
