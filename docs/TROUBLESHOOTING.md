# 故障排查

| 现象 | 处理 |
| --- | --- |
| `colab sessions` 要求授权 | 浏览器里的 Colab 登录不会自动授权 CLI。账号持有人需在 Mac 终端完成 Google OAuth，并把授权码粘贴回终端；不要发到聊天或提交到 Git。 |
| 隧道脚本提示没有单个 CLI 会话 | 先检查 `.venv/bin/colab sessions`。脚本故意拒绝 0 个、多个或未知 `?` 会话，避免 `--proxy-mode -s` 意外新建计费机器。 |
| SSH 返回 404 / 功能不可用 | 该 Colab 运行时可能未开放官方 SSH 端点。先核对 CLI 会话名称；持续失败则改用 Drive 下载 MP4 并手动导入画布。 |
| SSH 返回 429 | 该运行时可能已有 CLI SSH 连接（例如正用它复制模型）。等现有连接结束再启动隧道，不要并发重试或另开 GPU。 |
| 本机 8188 被占用 | 设置 `LOCAL_PORT=18188 scripts/connect_colab_h3.sh`，并把画布渠道地址改为 `http://127.0.0.1:18188`。 |
| Mac curl 200，但画布仍连接失败 | 检查浏览器 Origin 是否与 ComfyUI 的 `--enable-cors-header` 值完全一致；查看浏览器网络错误与 `/ws` 是否升级成功。 |
| `/prompt` 返回 `node_errors` | 核对所选工作流与当前模型、LoRA、编码器、双 VAE、ComfyUI 节点版本。不要用无限画布的 6 步 SelfLift 内置工作流代替这里的 4 步 Turbo 工作流。 |
| 工坊选择 JSON 后仍停在上传页 | 原版 v0.25.0 的适配器接口不匹配。按 [画布补丁说明](CANVAS_PATCH.md) 检查并应用；已有 `071cdf9` 不要重复应用。人工选择文件不需要修改浏览器“允许访问文件网址”设置。 |
| 视频节点仍显示 SelfLift | 核对渠道设置的“首尾帧视频工作流 (Frame Video)”默认值是否为导入的自定义工作流。节点标签本身不足以证明实际提交内容；查看任务对应的 ComfyUI `/history` 和提交 JSON。 |
| 画布显示成功但音频或规格不明 | 下载实际 MP4，用 `ffprobe -show_streams -show_format` 检查视频尺寸、时长和音频流；不要仅凭预览确认。 |
| Colab 恢复脚本长时间无输出 | Drive 到本地 SSD 复制约 41.38 GiB，先看 `colab sessions`、磁盘占用和已有进程。不要盲目并发重跑。 |
| `GET /system_stats` 是 200 但 CORS 不对 | `restore_colab.py` 会复用已运行 ComfyUI，不会改变其启动参数。核对实际 Origin，正常停止旧 ComfyUI 后以 `--enable-cors-header` 指定画布 Origin 重启。 |
| 成片只留在 Colab | 先保存到 Drive，再结束运行时。Colab 本地盘会随运行时销毁。 |

连接排查优先运行 `python3 scripts/check_connection.py`；它只检查 `GET /system_stats`、CORS 和 WebSocket 101，不提交推理。不要向公网开放无认证的 ComfyUI 8188 端口。停止运行时后再用 `colab usage` 核对当前消耗率归零。
