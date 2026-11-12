# Infinite Canvas v0.25.0 工作流导入修复

本包附带 `patches/infinite-canvas-workflow-studio.patch`，只修改 `web/src/pages/community/studio.tsx`。v0.25.0 工作流工坊使用了旧适配器字段，选择 JSON 后可能仍停在上传页；该补丁使它使用当前 `ingestWorkflow` 返回值。用户现有 Mac 项目已经包含提交 `071cdf9`，**无需再次应用**。

对其他原版 v0.25.0 检出，先备份/提交自己的修改，再在画布仓库根目录执行：

```bash
git status --short
git apply --check /path/to/colab-h3-infinite-canvas/patches/infinite-canvas-workflow-studio.patch
git apply /path/to/colab-h3-infinite-canvas/patches/infinite-canvas-workflow-studio.patch
bun run build
```

如果 `git apply --check` 失败，先检查是否已经有此修复或上游源码不同；不要用 `--force`、重置 Git 或覆盖工作区文件。应用补丁后按自己的项目流程提交、重启画布服务，再去“开源社区 → 工作流适配工坊”导入本包工作流。这个补丁只解决工坊导入接口不匹配，不能保证云端模型、隧道或画布生成成功。
