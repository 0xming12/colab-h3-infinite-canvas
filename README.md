# Colab H3 × Infinite Canvas

让普通电脑也能通过无限画布，调用云端 GPU 生成高质量 AI 视频。

这是一个开源的 AI 视频生成解决方案，将 **Google Colab、ComfyUI、MiniMax H3 和 Infinite Canvas（无限画布）** 整合成一套完整的创作工作流。

无需在本地部署大型视频模型，也无需购买昂贵的高性能显卡。通过 Google Colab 提供的云端 GPU 运行 MiniMax H3，再利用安全的 SSH 隧道连接本地无限画布，即可在可视化界面中完成图片导入、工作流配置、视频生成及结果管理。

## ✨ 核心功能

- **云端 GPU 加速**：利用 Google Colab A100 运行 MiniMax H3 视频生成模型。
- **无限画布创作**：接入 Infinite Canvas，以可视化方式组织素材和视频生成任务。
- **ComfyUI 工作流**：提供经过独立推理验证的 5 秒、10 秒视频生成工作流，支持 4 步 Turbo LoRA；另有新增的 8 步 Turbo LoRA 版本供对比。
- **原生音视频生成**：独立测试已成功输出包含 AAC 音轨的 MP4 视频。
- **文生图 / 图生图接视频**：新增 Qwen-Image-2.1 INT8 工作流，可在画布内先出图、再把图片接入首尾帧视频节点。
- **环境快速恢复**：提供自动安装、模型恢复和服务启动脚本，减少重复部署工作。
- **Google Drive 存储**：支持模型权重持久化，并提供视频与新增权重的备份脚本。
- **安全远程连接**：通过官方 Colab CLI SSH 隧道连接，无需暴露公网 ComfyUI 接口。

## 🚀 已验证效果

在 NVIDIA A100 80GB 环境中，已完成两组独立推理测试：

| 视频规格 | 实测生成耗时 |
| --- | --- |
| 5 秒 · 960×544 | 约 52 秒 |
| 10 秒 · 1344×768 | 约 253 秒 |

以上为独立 ComfyUI 推理结果，不代表无限画布端到端生成耗时。无限画布连接及工作流导入已验证，完整画布生成结果仍有待进一步独立验收。

## 🎯 项目目标

降低开源 AI 视频生成的使用门槛，让没有高端显卡的创作者，也能够利用云端算力和无限画布，搭建属于自己的 AI 视频创作工作台。

Open Source · Cloud GPU · ComfyUI · MiniMax H3 · Infinite Canvas

---

## 工作原理

在 Colab A100 的 ComfyUI 运行真实 MiniMax H3，通过官方 Colab CLI SSH 将只监听云端本机的 8188 端口转发到 Mac，再由 [Infinite Canvas](https://github.com/ZhuYichuan/infinite-canvas) 的 ComfyUI 渠道提交图生视频任务。

## 当前证据

| 项目 | 状态 |
| --- | --- |
| 独立 H3 推理 | **已实测**：5 秒 960×544 和 10 秒 1344×768，MP4 均有原生 AAC 音轨 |
| CLI SSH、HTTP、CORS、WebSocket | **已实测**：Mac `GET /system_stats` 为 200，限制画布 Origin 的 CORS 响应头正确，`/ws` 升级为 101 |
| 画布导入工作流 | **已实测**：适配补丁安装后识别 23 节点、26 连线，保存为自定义首尾帧工作流并设为默认 |
| 画布发起视频生成 | **用户报告成功**；本仓库尚无该次任务的 `/prompt`、`/history`、下载 MP4、声轨和规格独立核验记录 |
| 新运行时一键恢复 | 安装、模型复制、启动和节点检查各阶段已分别执行；`restore_colab.py` 在全新运行时连续执行尚未实测 |

完整操作按 [日常使用流程](docs/RUNBOOK.md) 从头进行。先看 [实测记录](docs/TEST_RESULTS.md) 和 [限制](docs/CONNECT.md)，不要把用户确认的画布生成写成已核验的 10 秒 720P 画布成片。

**新增部署：**[8 步 H3 + Qwen-Image-2.1 生图、图生图接视频](docs/UPGRADE_8STEP_QWEN.md)。权重已安装、Drive 备份校验通过，画布文生图、图生图与首尾帧视频的默认工作流已配置；8 步视频和 Qwen 生成效果由用户测试。

## 内容

```text
notebooks/Colab-H3-Deploy.ipynb   Colab 部署和独立推理
scripts/setup_mac.sh              在仓库内安装官方 CLI 0.8.0
scripts/restore_colab.py          从 Drive 恢复模型、安装并启动 ComfyUI
scripts/connect_colab_h3.sh       只连接已有单个 CLI 会话的本地 SSH 隧道
scripts/check_connection.py       不发起推理的 HTTP、CORS、WebSocket 检查
scripts/backup_outputs.py         将新 MP4 校验后备份到已挂载 Drive（尚未现场验收）
scripts/backup_new_models.py      校验并备份新增的 H3/Qwen 权重（尚未现场验收）
patches/infinite-canvas-workflow-studio.patch  修复 v0.25.0 工作流工坊导入
workflows/h3_5s_api.json          已独立推理的 5 秒工作流
workflows/h3_10s_720p_api.json   已独立推理的 10 秒工作流
workflows/h3_*_8step_api.json     待实测的 8 步 H3 工作流
workflows/qwen_image_2_1_t2i_api.json  待实测的 Qwen 生图工作流
workflows/qwen_image_2_1_i2i_api.json  待实测的 Qwen 单参考图编辑工作流
docs/RUNBOOK.md                   从启动到备份、停止的逐步流程
docs/CONNECT.md                   安全连接原理及验收边界
docs/TEST_RESULTS.md              实测指标
docs/TROUBLESHOOTING.md           故障排查
```

## 安全和发布

此包不含权重、MP4、Drive 文件、授权码或令牌。`.gitignore` 排除这些内容。ComfyUI 只监听 `127.0.0.1:8188`，SSH 仅转发到 Mac 本机，不能公开未认证接口。安装脚本固定上游版本，运行前可逐行检查；Google 授权由账号持有人自己完成。

仓库自有代码和文档使用 [MIT](LICENSE)。权重遵循 [MiniMax H3 Community License](https://huggingface.co/Comfy-Org/MiniMax-H3)；商业用途请先核对其许可。上游 ComfyUI、Colab CLI 和 Infinite Canvas 各遵循自身许可。
