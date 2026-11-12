# 日常使用：从启动到保存

以下命令在 Mac“终端”中运行；从仓库根目录开始。`colab new` 会开始消耗计算单元。先查看已有会话与余额，已有适用会话就复用，不要重新申请 A100。账号、Drive 授权只在 Google 页面和自己的终端完成。

## 1. 准备 Mac

```bash
cd /path/to/colab-h3-infinite-canvas
bash scripts/setup_mac.sh
.venv/bin/colab sessions
.venv/bin/colab usage
```

首次 `sessions` 会提供 Google 授权入口。把授权码只粘贴回终端，看到会话列表或 `No active sessions found on server` 才算成功。CLI 版本固定为 0.8.0。

## 2. 复用或创建运行时

如果列表中有本项目的 CLI A100 会话，记录其名称并继续。仅在没有可复用会话且预算允许时创建：

```bash
.venv/bin/colab new -s h3-canvas --gpu A100 --high-mem
.venv/bin/colab sessions
.venv/bin/colab usage
```

本流程默认名称 `h3-canvas`；如果已有会话是其他名称，在下述命令中替换。A100 高内存的分配取决于账户和平台当时的可用性，不能保证。

## 3. 挂载 Drive 并恢复环境

```bash
.venv/bin/colab drivemount -s h3-canvas
.venv/bin/colab exec -s h3-canvas --timeout 0 -f scripts/restore_colab.py
```

Drive 授权由账号持有人在 Google 页面确认。恢复脚本先复用 `/content/ComfyUI`、本地完整权重，再从 `MyDrive/Colab-H3/models/` 复制缺失文件；Drive 无备份时才从官方仓库下载。它固定 ComfyUI 和插件提交，启动只监听 `127.0.0.1:8188` 的服务，并校验必需节点。它**不发起视频推理**。首次完整一键执行尚未在全新运行时连续复测；如失败，按 Notebook 的环境单元逐步执行并看 [排障](TROUBLESHOOTING.md)。不要因输出暂时安静而重复执行，41.38 GiB 模型复制需要时间。

如需云端独立推理，打开 `notebooks/Colab-H3-Deploy.ipynb`，按单元运行。5 秒和 10 秒 API JSON 分别在 `workflows/`；生成任务会消耗额外计算单元。

## 4. 连接 Mac 画布

在第一个终端保持隧道运行：

```bash
bash scripts/connect_colab_h3.sh
```

另开一个终端执行只读健康检查：

```bash
python3 scripts/check_connection.py
```

期望 HTTP 200、CORS Origin `http://127.0.0.1:3000`、WebSocket 101。脚本不会发 `/prompt`。若 Mac 8188 被占用，可用 `LOCAL_PORT=18188 bash scripts/connect_colab_h3.sh`，然后用 `COMFY_URL=http://127.0.0.1:18188 python3 scripts/check_connection.py`；画布渠道地址也改为同一端口。

## 5. 导入工作流到 Infinite Canvas

1. 启动画布，打开 `http://127.0.0.1:3000`。在渠道设置中确认 ComfyUI 地址是 `http://127.0.0.1:8188`，看到连接状态正常。
2. 画布 v0.25.0 若尚未包含 `071cdf9` 工作流工坊修复，先按 [画布补丁说明](CANVAS_PATCH.md) 应用。已包含该提交的本地项目不要重复打补丁。
3. 打开“开源社区 → 工作流适配工坊”，点“浏览本地文件”，选 `workflows/h3_10s_720p_api.json`。出现节点图（实测 23 节点、26 连线）后保存为自定义工作流，例如 `MiniMax H3 Colab 10秒 720P Turbo`。
4. 到渠道配置，找到“首尾帧视频工作流 (Frame Video)”，把这个自定义工作流设为默认。截图或导出配置以便以后核对。画布视频节点里显示的内置 SelfLift 名称**不能证明**提交时用了 Turbo；实际执行工作流须从 ComfyUI `/history/{prompt_id}` 与提交 JSON 核对。

浏览器自动化可能无法代替用户选择本地文件。用户直接点击系统文件选择框即可，无需修改 Chrome 的安全设置。

## 6. 生成与验收

1. 导入参考 PNG/JPEG，拖出图片节点右侧连接点，选择“视频生成”，确认图片已连接到视频节点。
2. 选择“首尾帧 (Frame)”模式；首轮建议 5 秒、960×544，输入提示词，提交一次。观察任务进度、结果或错误。第二轮再选 10 秒、1344×768；这个尺寸在独立 H3 推理中已成功，画布路径尚待单独验收。
3. 打开生成视频预览，下载 MP4 到 Mac。若要确认原生音频、时长和规格，使用 `ffprobe` 核对视频和音频流；仅见到画面或“成功”提示不足以证明这些指标。
4. 在画布中保存工程并导出备份。下载 MP4 到 Mac，并保存参考图与对应工作流 JSON。Colab 的 `ComfyUI/output/` 是临时盘；可在第二个终端执行以下命令，把其中新增的 MP4 复制到已挂载的 Drive，按 SHA-256 检查且不覆盖不同内容的同名文件：

   ```bash
   .venv/bin/colab exec -s h3-canvas --timeout 0 -f scripts/backup_outputs.py
   ```

   这个新备份脚本已通过本地样例的复制、重复跳过和同名冲突保护测试，尚未在实际 Colab 输出上运行验收。它只备份 ComfyUI 输出目录中的 MP4，不备份画布浏览器本地工程；画布工程仍需手动导出。不要假定画布结果已经自动备份到 Drive。

## 7. 结束计费

先确认成片、工作流和画布工程已保存，再在隧道终端按 `Ctrl-C`。用户决定不再使用 A100 时执行：

```bash
.venv/bin/colab stop -s h3-canvas
.venv/bin/colab sessions
.venv/bin/colab usage
```

以 `sessions` 已无该会话、`usage` 当前消耗率为零为准。停止运行时会清除 Colab 本地盘；不要在输出尚未备份时停止。
