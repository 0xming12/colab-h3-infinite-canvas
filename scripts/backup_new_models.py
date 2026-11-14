"""Back up the new H3 8-step and Qwen-Image-2.1 weights to mounted Drive once."""
from pathlib import Path
import hashlib
import shutil

local = Path("/content/ColabH3/models")
drive = Path("/content/drive/MyDrive/Colab-H3/models")
files = (
    "loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
    "diffusion_models/qwen_image_2.1_int8_convrot.safetensors",
    "text_encoders/qwen3vl_8b_int8_convrot.safetensors",
    "vae/qwen_image_2.1_vae_bf16.safetensors",
)
if not drive.parent.is_dir():
    raise SystemExit("Drive 未挂载；先运行 colab drivemount")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.digest()


missing = []
for rel in files:
    src, dst = local / rel, drive / rel
    if not src.is_file():
        raise SystemExit(f"本地模型缺失：{src}")
    if dst.exists():
        if dst.stat().st_size != src.stat().st_size or sha(dst) != sha(src):
            raise SystemExit(f"Drive 同名模型内容不同，未覆盖：{dst}")
        print("已有相同备份，跳过：", rel)
    else:
        missing.append((src, dst))
need = sum(src.stat().st_size for src, _ in missing)
if shutil.disk_usage(drive.parent).free < need:
    raise SystemExit(f"Drive 可用空间不足：需要至少 {need / 2**30:.2f} GiB")
for src, dst in missing:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    if tmp.exists():
        raise SystemExit(f"发现未完成备份，先检查：{tmp}")
    shutil.copy2(src, tmp)
    if sha(tmp) != sha(src):
        raise SystemExit(f"校验失败，保留临时文件待检查：{tmp}")
    tmp.rename(dst)
    print("已备份：", rel)
print("新增模型备份完成；未覆盖原文件。")
