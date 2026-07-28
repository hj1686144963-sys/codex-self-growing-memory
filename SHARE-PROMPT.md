# 给同事的一次性安装提示词

请安装我提供的 `codex-self-growing-memory` 插件包。

执行要求：

1. 先运行 `python3 scripts/verify_package.py` 检查包体完整性。
2. 再运行 `python3 scripts/install.py --yes`。
3. 所有权限申请都暂停并让我点击确认，不得绕过系统授权。
4. 合并现有 `~/.codex/config.toml` 与当前生效的全局 AGENTS 文件；若存在非空
   `AGENTS.override.md` 必须写入该文件，否则写入 `AGENTS.md`，不得覆盖原内容。
5. 若已存在知识库，先询问我路径，再使用 `--vault` 安装。
6. 安装后运行 `python3 scripts/verify.py`。
7. 必须确认 Hook 已注册到用户级 `~/.codex/hooks.json`，不能只把插件加入
   Marketplace；只有原生 Memories、有效全局规则、用户级 Hooks、Hook 运行脚本、
   知识库模板、插件和 Marketplace 全部通过，且输出
   `"zero_trigger_ready": true`，才回复安装完成。
8. 若任一项失败，保留备份并告诉我失败项，不得假装成功。
9. 最后提醒我重启 Codex，并在首次 Hook 审核中点击一次信任；完成后新建聊天、
   新建项目和切换项目都不得要求我再发送任何触发指令。
