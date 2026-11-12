#!/bin/bash
# Forward local ComfyUI port to ONE existing CLI-managed Colab runtime.
# Never creates or stops a Colab runtime.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COLAB_BIN="${COLAB_BIN:-$ROOT/.venv/bin/colab}"
LOCAL_PORT="${LOCAL_PORT:-8188}"

if [ ! -x "$COLAB_BIN" ]; then
    echo "Colab CLI 不存在，请先运行 scripts/setup_mac.sh" >&2
    exit 1
fi

sessions="$("$COLAB_BIN" sessions)" || exit 1
active="$(printf '%s\n' "$sessions" | grep -E '^\[[^]]+\] .* \| Hardware:' || true)"
count="$(printf '%s\n' "$active" | grep -c . || true)"
if [ "$count" != 1 ] || printf '%s\n' "$active" | grep -q '^\[?\]'; then
    echo "需要恰好一个由 Colab CLI 创建的活动会话；当前会话：" >&2
    printf '%s\n' "$sessions" >&2
    exit 1
fi

case "$LOCAL_PORT" in
    ''|*[!0-9]*) echo "LOCAL_PORT 必须是数字" >&2; exit 1 ;;
esac
if /usr/sbin/lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "本机端口 $LOCAL_PORT 已被占用，未启动隧道。" >&2
    exit 1
fi

key_dir="$(mktemp -d /private/tmp/colab-h3-ssh.XXXXXX)"
trap 'rm -rf "$key_dir"' EXIT
ssh-keygen -q -t ed25519 -N '' -f "$key_dir/id_ed25519"
proxy="$(printf '%q ssh --proxy-mode -i %q' "$COLAB_BIN" "$key_dir/id_ed25519")"

echo "连接现有 Colab 会话；本机 ComfyUI 地址：http://127.0.0.1:$LOCAL_PORT"
echo "按 Ctrl-C 只关闭隧道，不停止 Colab 运行时。"
ssh -i "$key_dir/id_ed25519" \
    -o "ProxyCommand=$proxy" \
    -o "IdentitiesOnly=yes" \
    -o "StrictHostKeyChecking=accept-new" \
    -o "UserKnownHostsFile=$key_dir/known_hosts" \
    -o "ExitOnForwardFailure=yes" \
    -o "ServerAliveInterval=15" \
    -o "ServerAliveCountMax=3" \
    -N -L "127.0.0.1:$LOCAL_PORT:127.0.0.1:8188" root@colab-h3
