# Codex Self-Growing Memory 1.1.0

这是第一个面向公开分享的零触发版本。

安装并完成一次 Hook 信任后，Codex 会在新建聊天、新建项目和切换工作目录时自动加载跨会话记忆、项目知识和防踩坑规则，不需要再次输入固定触发指令。

## 本版重点

- 用户级自动 Hooks；
- 自动适配 `AGENTS.md` 与 `AGENTS.override.md`；
- 原配置合并、备份与回滚；
- 按需知识检索和敏感信息过滤；
- `zero_trigger_ready: true` 端到端验收。

## 安装

下载并解压 `codex-self-growing-memory-1.1.0.zip`，将整个文件夹交给 Codex，然后发送 `SHARE-PROMPT.md` 中的安装提示词。

安装后重启 Codex，并在首次 Hook 审核中点击一次信任。
