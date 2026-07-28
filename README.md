# Codex Self-Growing Memory

让 Codex 在新建聊天、新建项目和切换工作目录后，自动继续使用历史记忆、项目知识与防踩坑经验，无需反复输入触发指令。

[![Version](https://img.shields.io/badge/version-1.1.0-36d399)](https://github.com/hj1686144963-sys/codex-self-growing-memory/releases)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Codex](https://img.shields.io/badge/OpenAI-Codex-111827)](https://openai.com/codex/)

> Automatically carry durable context, project decisions and anti-regression lessons across local Codex chats—without a trigger phrase.

## 它解决什么问题

普通对话结束后，下一次新建聊天往往需要重新解释项目背景、个人偏好、已经确认的方案和踩过的坑。这个插件把这些信息放到可检查、可迁移的本地机制中：

- 开启 Codex 原生跨会话 Memories；
- 为所有新聊天和新项目加载用户级 AGENTS 规则；
- 在会话开始时自动注入工作机制；
- 根据当前问题只检索少量相关知识，避免全库扫描浪费 Token；
- 将稳定决策、项目状态、方法和错误经验沉淀到 Markdown / Obsidian 知识库；
- 安装前备份原配置，支持验证、重复安装和一键回滚。

## 零触发是如何实现的

核心自动加载不依赖手动调用 Skill，也不把“加入 Marketplace”误认为插件已经启用。安装器会在当前 `CODEX_HOME` 中配置：

1. 原生 Memories；
2. 当前真正生效的用户级 `AGENTS.md` 或 `AGENTS.override.md`；
3. 用户级 `~/.codex/hooks.json`；
4. `SessionStart`、`UserPromptSubmit` 和 `SessionEnd` Hook；
5. 本地知识库与运行配置。

首次安装后，Codex 会要求审核 Hook。使用者点击一次信任并重启 Codex 后，新建聊天、新建项目和切换工作目录都不需要再输入固定口令。

## 安装

### 方式一：让 Codex 帮你安装

1. 从 [Releases](https://github.com/hj1686144963-sys/codex-self-growing-memory/releases) 下载最新版 ZIP。
2. 解压后在 Codex 中打开整个文件夹。
3. 把 [SHARE-PROMPT.md](SHARE-PROMPT.md) 的内容发给 Codex。
4. 按提示点击权限确认；安装完成后重启 Codex，并在首次 Hook 审核中点击信任。

### 方式二：终端安装

需要 Python 3.9 或更高版本。

```bash
python3 scripts/verify_package.py
python3 scripts/install.py --yes
python3 scripts/verify.py
```

如果要连接已有 Markdown / Obsidian 知识库：

```bash
python3 scripts/install.py --yes --vault "/你的知识库绝对路径"
python3 scripts/verify.py
```

只有验证结果同时出现以下内容，才表示零触发机制准备完成：

```json
{
  "status": "pass",
  "zero_trigger_ready": true
}
```

## 安全与隐私

- 知识检索完全在本机运行，不把知识库内容发送给插件作者；
- 默认跳过 `.env`、认证文件和常见敏感目录；
- 注入上下文前会过滤 API Key、Token、密码、Cookie 和私钥模式；
- 不会绕过 Codex 的沙箱、外部写入或发布授权；
- 安装器合并而不是覆盖已有配置，安装前自动保留备份。

## 回滚

```bash
python3 scripts/rollback.py --latest
```

回滚会恢复安装前的 Codex 配置，但不会删除已经产生的知识库内容。

## 适用范围

- 使用同一 `CODEX_HOME` 的本地 Codex App 与 Codex CLI；
- 已在 macOS 上完成安装、重复安装、回滚和 ZIP 解压验收；
- Windows 与 Linux 需要可用的 Python 3，建议安装后运行完整验证；
- ChatGPT 网页版使用独立云端记忆，不读取本机 Codex Hooks；
- 管理员策略可以禁用用户 Hooks，插件不会绕过组织安全策略。

## 项目结构

```text
codex-self-growing-memory/
├── .codex-plugin/plugin.json
├── skills/codex-auto-memory/
├── scripts/
│   ├── install.py
│   ├── memory_hook.py
│   ├── verify.py
│   ├── verify_package.py
│   └── rollback.py
├── assets/knowledge-base/
├── docs/ARCHITECTURE.md
└── SHARE-PROMPT.md
```

## 参与改进

欢迎提交 Issue 或 Pull Request。报告问题时请勿上传真实 Token、Cookie、私钥、公司内部文档或完整私人知识库。

## License

[MIT License](LICENSE)
