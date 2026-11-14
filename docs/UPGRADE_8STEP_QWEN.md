# 8 步 H3 + Qwen-Image-2.1 生图接视频

## 已准备的工作流

- `workflows/h3_5s_8step_api.json`、`h3_10s_720p_8step_api.json`：保留原 H3 主模型、文本编码器、双 VAE 与音频链路，采样改为 8 步，并**同时**改用官方 `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors`。原 4 步 JSON 不覆盖，便于对比。
- `workflows/qwen_image_2_1_t2i_api.json`：Qwen-Image-2.1 INT8 ConvRot 生图，8B INT8 文本编码器、Qwen VAE，25 步、CFG 1、1344×768，输出 PNG。独立 API JSON 为按官方节点结构整理的候选工作流，**尚未在 GPU 上推理验证**。
- `workflows/qwen_image_2_1_i2i_api.json`：复用同三份 Qwen 权重，`LoadImage` 接到 `TextEncodeQwenImage21` 的 `images.image_1`，由编码节点输出与参考图尺寸匹配的 latent；25 步、CFG 1、1024 像素预算。当前仅接 1 张参考图，**尚未在 GPU 上推理验证**。

仅把 4 步工作流的 `steps` 改为 8 而保留 4 步 Turbo LoRA 不是本方案。8 步也不保证效果一定改善；需同参考图、提示词和种子对照输出。

## 2026-11-13 实际部署状态

- 用户亲自授权并挂载 Drive；A100 80GB、高内存运行时 `h3-canvas` 启动。ComfyUI 0.45.0 识别 784 个节点，H3 与 `TextEncodeQwenImage21` 节点齐全。
- H3 既有五个权重从 Drive 复用；8 步 LoRA 与 Qwen 三个权重下载到 Colab 本地 SSD。ComfyUI `/object_info` 中四个新增权重名称均可选。新增权重在 Drive 中的备份与本地文件逐个 SHA-256 一致。
- 官方 Colab CLI SSH 本地隧道已连接；Mac `GET /system_stats` 为 200，CORS Origin 正确，`/ws` 为 101。画布渠道“测试连接”提示成功。
- 画布工坊导入并保存 Qwen INT8 文生图（识别 `t2i`，9 节点）及 H3 8 步 10 秒（识别 `frameVideo`，23 节点），分别设为各自类别默认。原 4 步工作流和现有画布工程保留。
- 2026-11-13 又导入并保存 Qwen INT8 单参考图编辑（9 节点、11 连线），手动选为 `i2i` 类别并设为图生图默认。工坊的自动分类先把它判为 `t2i`，因为已有标注槽位触发了早期验证；手动指定 `i2i` 后保存成功。此项仅验证画布导入与配置，尚未验证生成。
- **未执行生成任务**，按用户要求由用户自行测试效果。权重出现在模型列表不等于已完成真正推理。
- 最后查询：余额 167.99 CCU，消耗率 8.88 CCU/小时；A100 留给用户测试。测试结束须保存成片并停止运行时。

## 恢复模型

先按 [RUNBOOK.md](RUNBOOK.md) 授权 CLI、查看余额、创建 A100 并亲自挂载 Drive。然后运行：

```bash
.venv/bin/colab exec -s h3-canvas --timeout 0 --env ENABLE_QWEN_IMAGE21=1 -f scripts/restore_colab.py
```

恢复脚本优先复用本地盘和 Drive 已有模型。H3 新增 8 步 LoRA 约 1.82 GiB；Qwen 新增三个权重约 16.1 GiB，源自 [MiniMax H3 官方 ComfyUI 权重](https://huggingface.co/Comfy-Org/MiniMax-H3) 和 [Qwen-Image-2.1 官方 ComfyUI 权重](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)，均固定到仓库提交。模型在 Colab SSD 上运行；确认 Drive 空间足够后，可执行 `scripts/backup_new_models.py` 保存新增权重：

```bash
.venv/bin/colab exec -s h3-canvas --timeout 0 -f scripts/backup_new_models.py
```

不要同时运行两次恢复或备份命令。恢复脚本会复用健康的 ComfyUI；若旧进程缺少新节点，应检查 `/object_info`，必要时更新或正常重启 ComfyUI。**本次没有执行新模型推理**，不能把文件识别当作生成成功。

## 无限画布组合

1. 保留现有 ComfyUI 渠道地址和 SSH 隧道。打开“工作流适配工坊”，导入 Qwen JSON，确认识别为文生图 (`t2i`) 后保存；在渠道配置把它设为“文生图工作流 (T2I)”默认。
2. 再导入 H3 8 步 10 秒 JSON，确认识别为首尾帧视频 (`frameVideo`) 后保存并设为“首尾帧视频工作流 (Frame Video)”默认。原 4 步工作流仍保留，不覆盖。
3. 在画布创建文本生图节点，输入图像提示词并生成；检查图片真正回到画布。把该图片节点连接到视频节点，设为“首尾帧 (Frame)”模式，输入运动和声音提示词，先生成 5 秒低分辨率，确认云端提交的 LoRA/步数以及视频、音轨；再尝试 10 秒 1344×768。
4. 下载 PNG 和 MP4，导出画布工程；使用 `ffprobe` 查 MP4 的尺寸、时长和音频流。按 [RUNBOOK.md](RUNBOOK.md) 备份云端输出并停止运行时。

画布中视频节点显示的内置模型标签不能证明实际使用了导入的 8 步 JSON；应查任务的 ComfyUI 提交记录。首尾帧模式在**没有节点级显式工作流选择**时使用渠道的 8 步默认；已有节点若显式保留旧工作流 ID，则按该 ID 执行。Qwen 图生图现为单参考图；画布内置 Qwen 模型配置最多 10 张，Qwen-Image-2.1 节点最多 16 张，当前自定义工作流仍只绑定 1 张。多图与自动串行批量任务尚未部署。

## 实测边界与费用

2026-11-13 初次查询时没有活动 Colab 会话，余额 171.26 CCU、消耗率 0。第一次临时 A100 因用户当时无法授权 Drive 已停止，未下载新权重。用户回到电脑前后再次启动并完成本页部署；最后一次余额 167.99 CCU、消耗率 8.88 CCU/小时。等待授权期间不应让 A100 空转；测试结束务必停止当前会话。
