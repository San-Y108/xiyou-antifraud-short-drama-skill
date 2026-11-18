# 必需技能的检查与安装

本工作流强制使用`short-drama-write`、`short-drama-storyboard`、`short-drama-review`。来源为[ZenStory AI公开仓库](https://github.com/zenstory-ai/drama-skills)，上游MIT；下载版本在同目录`dependencies.lock.json`锁定，已有技能不强制降级／覆盖。

## 决策顺序

1. 在宿主实际技能目录寻找三个目录里的`SKILL.md`，读取确认身份与用途，不能只凭名称在列表里出现就声称读过。
2. 缺少时安装到当前宿主使用的目录。用户启用此工作流并要求完整制作，已包含补齐这三项的意图；遵循宿主已有权限规则，不扩展到全局软件升级或替换已有技能。
3. 运行检查，再读取各依赖的`SKILL.md`和当前环节所需引用。安装后若宿主要求刷新才能发现，明确需要刷新；可直接读取新文件的环境可继续执行，不假装工具注册已经完成。
4. 安装失败时保留错误证据并说明缺项，不悄悄退化成“不用技能也一样”。不运行陌生下载地址的安装脚本，不暴露密钥。

## 自带安装器

以下命令从本技能文件夹运行，Python 3.9以上，标准库即可，不要求Node或其他Python包。

```bash
# Codex默认目录：仅检查，不改文件
python3 scripts/ensure_dependencies.py --check

# Codex默认目录：自动下载缺项，保留已有技能
python3 scripts/ensure_dependencies.py --install

# 其他宿主或自定义路径：明确指定实际技能目录
python3 scripts/ensure_dependencies.py --install --dest /实际使用的技能目录
```

默认目标为`$CODEX_HOME/skills`，未设置时为`~/.codex/skills`。Claude Code可指定`~/.claude/skills`，通用Agents环境可指定`~/.agents/skills`；以该宿主实际可发现路径为准，不同时向所有目录安装。

安装器只下载锁定公开仓库的代码归档，提取三个缺少的技能及其文件；校验路径、拒绝覆盖、保留上游许可证，不执行下载代码。已有同名目录不完整时报告异常，让用户选择修复，不自动删除或覆盖。

宿主已有官方安装器时可用其GitHub安装能力，来源、路径、锁定ref必须与`dependencies.lock.json`一致。不要拷贝本机绝对路径或别人的安装状态到新项目。

## 可验证的完成状态

记录三个技能的位置与可读状态；新下载项记录上游仓库与commit。只有读取后才写“已使用”。本技能安装器不管理即梦、Image或它们的账号／收费权限；这些能力缺失时另行说明，不安装不明第三方替代品。
