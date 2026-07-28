# Changelog

## 1.1.0 — 2026-07-28

- 将核心自动机制注册为用户级 Hooks，避免依赖插件手动启用。
- 自动识别并更新当前真正生效的 `AGENTS.md` 或 `AGENTS.override.md`。
- 新增 `zero_trigger_ready` 验证结果。
- 保留已有 Hooks、Codex 配置和全局规则，重复安装自动去重。
- 验证普通全局规则、override、回滚和最终 ZIP 解压安装。

## 1.0.0 — 2026-07-28

- 首次发布。
- 提供 Memories、全局规则、知识库模板、选择性检索、安装验证和回滚。
