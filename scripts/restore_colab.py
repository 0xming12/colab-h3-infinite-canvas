# Colab 专用环境恢复脚本；由已整理的 Notebook 环境单元生成。
# 需要在 Colab Python 环境中运行；不执行视频推理。

# ===== Notebook cell 1 =====
# ============ 单元 1：环境自检 ============
import os, sys, shutil, subprocess

print("=" * 68)
print("Colab-H3 环境自检")
print("=" * 68)

ok = True

# --- GPU ---
gpu_name, vram = None, 0.0
if shutil.which("nvidia-smi"):
    raw = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        capture_output=True, text=True).stdout.strip()
    print("GPU        :", raw)
    gpu_name = raw.split(",")[0].strip()
    try:
        vram = float(raw.split(",")[1].replace("MiB", "").strip()) / 1024
    except Exception:
        pass
else:
    print("GPU        : 未检测到")
    ok = False

# --- torch ---
try:
    import torch
    print("torch      :", torch.__version__, "| CUDA:", torch.version.cuda,
          "| 可用:", torch.cuda.is_available())
    if torch.cuda.is_available() and not vram:
        vram = torch.cuda.get_device_properties(0).total_memory / 2**30
except ImportError:
    print("torch      : 未安装")

print("显存       : %.1f GB" % vram)

if vram and vram < 20:
    ok = False
    print("\n  [不可行] 显存 < 20 GB。H3 剪枝底模 19.5 GB 无法加载。")
    print("           请到「代码执行程序 → 更改运行时类型」改选 L4 或 A100，再重跑本格。")

# --- 系统内存 ---
ram = 0.0
try:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemTotal"):
                ram = int(line.split()[1]) / 1024**2
                break
except Exception:
    pass
print("系统内存   : %.1f GB" % ram)
if ram and ram < 16:
    print("  [注意] 内存偏低。--disable-pinned-memory 已启用，但仍可能被 host OOM 杀掉。")

# --- 磁盘 ---
du = shutil.disk_usage("/content")
print("本地磁盘   : 可用 %.1f GB / 共 %.1f GB" % (du.free / 2**30, du.total / 2**30))

print("=" * 68)
print("结论:", "可以继续" if ok else "先解决上面的问题")
# ===== Notebook cell 2 =====
# ============ 单元 2：目录约定（权重走本地盘，Drive 用于备份）============
# 说明：权重 41.4 GB 放本地盘，读取比 Drive 快得多；Drive 保存模型、产物和日志。
#       Drive 挂不上 / 空间不够也不影响部署，只是产物不能持久化。
import os, shutil

LOCAL_ROOT = "/content/ColabH3"
COMFY_DIR  = "/content/ComfyUI"
BASE       = "http://127.0.0.1:8188"
MODELS_DIR = LOCAL_ROOT + "/models"
OUT_DIR    = LOCAL_ROOT + "/outputs"
LOG_DIR    = LOCAL_ROOT + "/logs"
HF_CACHE   = LOCAL_ROOT + "/hf_cache"
for d in (LOCAL_ROOT, MODELS_DIR, OUT_DIR, LOG_DIR, HF_CACHE):
    os.makedirs(d, exist_ok=True)

DRIVE_ROOT = None
try:
    from google.colab import drive
    if not os.path.exists("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    if os.path.exists("/content/drive/MyDrive"):
        DRIVE_ROOT = "/content/drive/MyDrive/Colab-H3"
        for sub in ("outputs", "workflows", "logs"):
            os.makedirs(os.path.join(DRIVE_ROOT, sub), exist_ok=True)
        free = shutil.disk_usage("/content/drive/MyDrive").free / 2**30
        print("Drive 可用 : %.1f GB" % free)
        print("Drive 目录 :", DRIVE_ROOT)
    else:
        print("Drive 挂载未完成，本次产物只留在本地")
except Exception as e:
    print("Drive 不可用（不影响部署）:", repr(e)[:200])

os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "60"
os.environ["HF_HOME"] = HF_CACHE
os.environ["HUGGINGFACE_HUB_CACHE"] = HF_CACHE
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

du = shutil.disk_usage("/content")
print()
print("本地盘可用 : %.1f GB" % (du.free / 2**30))
print("权重目录   :", MODELS_DIR)
print("产物目录   :", OUT_DIR)
print("日志        :", LOG_DIR)

# ===== Notebook cell 3 =====
# 单元 3：复用现有 ComfyUI；新环境安装到已实测提交
import os, subprocess, sys
COMFY_COMMIT = "4d64a8bc072b81c9b47321789b4d83fb7348ae2a"
ESSENTIALS_COMMIT = "9d9f4bedfc9f0321c19faf71855e228c93bd0dc9"

def clone_at_commit(url, path, commit):
    subprocess.run(["git", "clone", "--depth", "1", url, path], check=True)
    subprocess.run(["git", "-C", path, "fetch", "--depth", "1", "origin", commit], check=True)
    subprocess.run(["git", "-C", path, "checkout", "--detach", commit], check=True)

if not os.path.isdir(COMFY_DIR):
    clone_at_commit("https://github.com/Comfy-Org/ComfyUI.git", COMFY_DIR, COMFY_COMMIT)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(COMFY_DIR, "requirements.txt")], check=True)
else:
    print("复用现有 ComfyUI：", COMFY_DIR)
ess = os.path.join(COMFY_DIR, "custom_nodes", "ComfyUI_essentials")
if not os.path.isdir(ess):
    clone_at_commit("https://github.com/cubiq/ComfyUI_essentials.git", ess, ESSENTIALS_COMMIT)
    req = os.path.join(ess, "requirements.txt")
    if os.path.isfile(req):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req], check=True)
for sub in ("diffusion_models", "text_encoders", "vae", "loras"):
    os.makedirs(os.path.join(MODELS_DIR, sub), exist_ok=True)
    os.makedirs(os.path.join(COMFY_DIR, "models", sub), exist_ok=True)
print("ComfyUI:", subprocess.getoutput("git -C /content/ComfyUI rev-parse --short HEAD"))

# ===== Notebook cell 4 =====
# 单元 4：优先恢复 Drive 中完整权重，再从官方仓库补齐
import os, time, shutil
try:
    from huggingface_hub import hf_hub_download
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'huggingface_hub'], check=True)
    from huggingface_hub import hf_hub_download
REPO = "Comfy-Org/MiniMax-H3"
MODEL_REVISION = "54472221d27c695fca9621b0c3ed52f06c4af707"
FILES = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors", 19.53),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", 14.61),
    ("vae/minimax_h3_video_vae_fp16.safetensors", 4.85),
    ("vae/minimax_h3_audio_vae_fp32.safetensors", 0.564),
    ("loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", 1.822),
]
def complete(path, gib):
    return os.path.isfile(path) and os.path.getsize(path) >= gib * 2**30 * 0.97
for rel, gib in FILES:
    dst = os.path.join(MODELS_DIR, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not complete(dst, gib):
        saved = os.path.join(DRIVE_ROOT, "models", rel) if DRIVE_ROOT else None
        if saved and complete(saved, gib):
            print("从 Drive 恢复：", rel, flush=True)
            shutil.copy2(saved, dst)
        else:
            print("下载官方权重：", rel, flush=True)
            hf_hub_download(repo_id=REPO, filename=rel, revision=MODEL_REVISION, local_dir=MODELS_DIR)
    assert complete(dst, gib), "权重不完整：" + rel
    link = os.path.join(COMFY_DIR, "models", rel)
    if not os.path.exists(link):
        os.symlink(dst, link)
    print("就绪：", rel)

# ===== Notebook cell 5 =====
# 单元 5：复用或启动仅本机可访问的 ComfyUI
import os, subprocess, sys, time, requests
log_path = os.path.join(LOG_DIR, "comfyui.log")
CANVAS_ORIGIN = os.environ.get("CANVAS_ORIGIN", "http://127.0.0.1:3000")
def healthy():
    try:
        return requests.get(BASE + "/system_stats", timeout=5).status_code == 200
    except requests.RequestException:
        return False
if healthy():
    print("复用现有 ComfyUI：", BASE)
else:
    log = open(log_path, "ab")
    proc = subprocess.Popen([sys.executable, "main.py", "--listen", "127.0.0.1", "--port", "8188", "--disable-pinned-memory", "--disable-api-nodes", "--enable-cors-header", CANVAS_ORIGIN], cwd=COMFY_DIR, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(60):
        if healthy():
            break
        if proc.poll() is not None:
            raise RuntimeError("ComfyUI 退出：" + open(log_path, errors="replace").read()[-2000:])
        time.sleep(5)
assert healthy(), "ComfyUI 未就绪：" + open(log_path, errors="replace").read()[-2000:]
print("ComfyUI 版本：", requests.get(BASE + "/system_stats").json()["system"]["comfyui_version"])

# ===== Notebook cell 6 =====
# ============ 单元 6：环境校验（节点 / 模型 / 显存）============
import json, requests

need_nodes = {"UNETLoader", "CLIPLoader", "VAELoader", "LoraLoaderModelOnly",
              "MiniMaxH3ImageToVideo", "ComfyMathExpression", "SamplerCustomAdvanced",
              "BasicScheduler", "CreateVideo", "SaveVideo", "VAEDecode", "VAEDecodeAudio",
              "LoadImage", "PrimitiveInt", "PrimitiveStringMultiline",
              "BasicGuider", "KSamplerSelect", "RandomNoise"}

info = requests.get(BASE + "/object_info", timeout=60).json()
have = set(info.keys())
missing = sorted(need_nodes - have)
print("节点总数      :", len(have))
print("缺失必需节点  :", missing if missing else "无")

if "MiniMaxH3ImageToVideo" in info:
    req = info["MiniMaxH3ImageToVideo"].get("input", {})
    print("H3 节点输入   :", list(req.get("required", {}).keys()))

# 模型是否被 ComfyUI 识别到
def options(node, field):
    try:
        return info[node]["input"]["required"][field][0]
    except Exception:
        return []

for node, field, want in [
    ("UNETLoader", "unet_name", "minimax_h3_fl2va_pruned_int8_convrot.safetensors"),
    ("CLIPLoader", "clip_name", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("VAELoader", "vae_name", "minimax_h3_video_vae_fp16.safetensors"),
    ("LoraLoaderModelOnly", "lora_name", "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors"),
]:
    opts = options(node, field)
    print("%-22s %s -> %s" % (node, field, "OK" if want in opts else "未找到！"))

st = requests.get(BASE + "/system_stats", timeout=10).json()
for d in st.get("devices", []):
    print("设备: %s | 显存总量 %.1f GB | 空闲 %.1f GB" % (
        d.get("name"), d.get("vram_total", 0) / 2**30, d.get("vram_free", 0) / 2**30))
assert not missing, "缺少必需节点：" + ", ".join(missing)
