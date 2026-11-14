# 已有真实推理记录

本页表格均为原 **4 步 H3** 的历史实测。新增 8 步 H3 与 Qwen-Image-2.1 的准备和未测边界见 [升级流程](UPGRADE_8STEP_QWEN.md)；不要将下方耗时、显存或画质结果套用到新工作流。

2026-11-11 在 NVIDIA A100-SXM4-80GB、ComfyUI 0.45.0、PyTorch 2.14.1+cu130 上运行。使用 MiniMax H3 `int8_convrot` 主模型、Qwen3-VL NVFP4 AWQ 文本编码器、Video VAE、Audio VAE 与 4 步 Turbo LoRA。`/prompt` 返回 200、`node_errors` 为空，`/history` 显示执行成功。生成的 MP4 在原环境与 Mac 上通过 `ffprobe` 核对，并完成全片解码。

| 指标 | 5 秒工作流 | 10 秒工作流 |
| --- | ---: | ---: |
| 实际视频 | 960×544，5.166688 秒 | 1344×768，10.125 秒 |
| 帧率 / 帧数 | 24 fps / 124 帧 | 24 fps / 243 帧 |
| 编码 | H.264 + AAC 32 kHz 双声道 | H.264 + AAC 32 kHz 双声道 |
| ComfyUI 执行耗时 | 51.82 秒 | 253.40 秒 |
| GPU 显存峰值 | 41,968 MiB | 49,280 MiB |
| 系统已用内存峰值 | 13,081 MiB | 16,328 MiB |
| 采样 | 4 步 Turbo LoRA | 4 步 Turbo LoRA |

五个权重共 41.38 GiB，已在原项目的 Google Drive 中备份，源文件与备份文件字节数逐个一致。本公开仓库不含这些权重、视频、日志或个人 Drive 内容。观察到约 10.08 CCU 消耗，但结束运行时后的最终精确扣费未读取，因此不是账单数字。

## 后续连接实测

- 官方 `google-colab-cli==0.8.0` 已由账号持有人完成 OAuth；CPU 会话 SSH 命令实际返回 `COLAB_SSH_OK`，之后停机。
- 新建 CLI A100 高内存会话后，Drive 挂载成功。GPU 为 A100 80GB，系统 RAM 约 167 GiB，本地磁盘约 236 GB，PyTorch 2.14.1+cu130。ComfyUI 固定提交 `4d64a8bc072b81c9b47321789b4d83fb7348ae2a`、插件固定提交 `9d9f4bedfc9f0321c19faf71855e228c93bd0dc9`，模型五件从 Drive 复制至本地盘，ComfyUI 0.45.0 启动并识别 784 个节点，必需 H3 节点无缺失。
- Mac 通过包内 SSH 隧道对 `/system_stats` 请求返回 200；指定画布 Origin 的 CORS 头正确；`/ws` 握手返回 101。画布显示 GPU 使用情况。
- v0.25.0 工作流工坊经本包补丁修复后，实际导入 10 秒 API JSON：23 节点、26 连线，`frameVideo` 识别为 100%，保存为自定义工作流并设为该类别默认。
- 用户报告画布生成视频成功。尚未取得该画布任务的提交 JSON、`/history`、视频文件与 `ffprobe` 记录，因此不把它写为已独立验收的 10 秒 720P 原生音频画布成片。

恢复脚本的安装、Drive 模型复制、启动和检查阶段分别已执行；**未实测**在全新运行时一次连续执行 `restore_colab.py`。新加入的 `backup_outputs.py` 通过本地样例的复制、重复跳过和同名冲突保护测试，尚未在真实 Colab 成片上运行验收。声音轨道存在且可解码；主观声音质量没有人工听评。后续 A100 会话曾读取 `usage`：189.15 CCU、零消耗率（创建前），之后 184.92 CCU、8.88 CCU/小时（运行中）；这是两个时间点的状态，不是完整会话最终扣费。
