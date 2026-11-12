"""Run with `colab exec -f` after generation; copy new ComfyUI MP4s to Drive.

Requires the account holder to have mounted Drive. Does not overwrite existing files.
"""
from pathlib import Path
import hashlib
import shutil

source = Path("/content/ComfyUI/output")
target = Path("/content/drive/MyDrive/Colab-H3/outputs/comfyui")
if not source.is_dir():
    raise SystemExit("ComfyUI 输出目录不存在；先确认运行时与生成结果")
if not target.parent.is_dir():
    raise SystemExit("Drive 未挂载；先运行 colab drivemount")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.digest()


copied = 0
for src in sorted(source.rglob("*.mp4")):
    dst = target / src.relative_to(source)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.stat().st_size == src.stat().st_size and digest(dst) == digest(src):
            print("已有相同文件，跳过：", dst)
            continue
        raise SystemExit(f"Drive 中存在不同内容的同名文件，未覆盖：{dst}")
    tmp = dst.with_name(dst.name + ".part")
    if tmp.exists():
        raise SystemExit(f"发现未完成的备份文件，先检查并处理：{tmp}")
    shutil.copy2(src, tmp)
    if digest(tmp) != digest(src):
        raise SystemExit(f"备份校验失败；保留临时文件待检查：{tmp}")
    tmp.rename(dst)
    print("已备份：", dst)
    copied += 1
print(f"本次新增备份 {copied} 个 MP4；原始文件仍留在 Colab 本地盘。")
