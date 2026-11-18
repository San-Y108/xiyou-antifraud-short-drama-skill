# 西游反诈竖屏短剧 Skill

把一个新的真实诈骗类型，做成与《三打白骨精：她还欠俺钱！》同系列的西游反诈短剧。**默认全自动做到最终MP4**，54秒目标、55秒硬上限、9:16、720P、国风少年漫；Image生图，Seedance 2.0 Fast VIP生成视频，中文聊天窗与字幕后期排版。

**这是可安装的Agent Skill，不是只给一份流程说明。** 必须调用剧本、分镜与审查技能；缺少时从锁定的公开上游自动下载缺项，再读取使用。用户主动启动并给出诈骗类型后，AI自行完成剧本审查、素材取舍、生成与合成，默认不等待阶段性人工审核。

## 安装

支持[Agent Skills](https://github.com/vercel-labs/skills)的环境：

```bash
npx skills add San-Y108/xiyou-antifraud-short-drama-skill
```

在安装界面选择本仓库的`xiyou-antifraud-short-drama`和实际使用的Agent。也可以直接把下面这段交给Codex的技能安装器：

> 请安装 https://github.com/San-Y108/xiyou-antifraud-short-drama-skill/tree/main/skills/xiyou-antifraud-short-drama ，然后按其中的依赖安装流程补齐剧本、分镜和审查技能。

也可下载Release，将`xiyou-antifraud-short-drama`文件夹放入当前宿主技能目录。Codex一般为`$CODEX_HOME/skills`或`~/.codex/skills`，其他宿主以实际目录为准。刷新宿主后使用；宿主能直接读取新文件时可先读取执行。

## 使用：换一个诈骗类型

```text
使用 $xiyou-antifraud-short-drama，诈骗类型：冒充客服退款。
```

**上面这一句即可启动到成片交付。** 案例和西游桥段未指定时由AI查证、选择；AI自行写作、审稿、分镜、生图、选片、视频生成、局部返工、文字合成、混音与验收，不在中途问“要不要继续”。

启动默认方案：Image使用当前可用配额；视频Seedance 2.0 Fast VIP、9:16、720P；即梦本项目所有提交报价累计上限3000积分，包含返工和状态不明任务。首条回复简短说明后直接开始，报价照常查询并计入预算，不等待重复确认。可在启动句修改预算。

只有超限、换收费工具、用户锁定要求必须变化，或登录／权限／必要人工操作等真实阻塞时才请求最少必要决定。平台或宿主强制的计费确认仍需遵守。仅下载、安装、询问用法或阅读模板不启动收费任务；费用依据当前用户主动发起的制作请求与选用的默认方案处理，不沿用别人的授权。

## 固定在技能里的制作偏好

| 要求 | 执行方式 |
| --- | --- |
| 前三秒吸引人 | 用经典关系中的反常行为建立冲突，后文兑现 |
| 有前情、不突兀 | 一个有用画面／短前情；闪回明确且通常一次 |
| 快节奏、多内容 | 压缩时间空档，动作与对白并行，保留必要因果 |
| 减少空白间隔 | 指对白／镜头的时间空档，不是删除标点或换行 |
| 必须使用剧本Skill | 写作、分镜、审查三项缺少就安装，不能跳过 |
| 西游内的取信与损失 | 用相关角色、头像、盘缠／仙丹／灵力等转译，标虚构 |
| Image与即梦分工 | Image人物及关键帧；指定即梦模型生成视频 |
| 中文无乱码 | 聊天窗、按钮、字幕后期中文排字，处理原生乱码层 |
| AI内部审查 | 写作、审查、修订、选片自动完成，不设逐阶段人工批准 |
| 全流程持续制作 | 当前制作范围内连续完成生成、检查、返工、合成与最终交付 |
| 积分可追踪 | 启动时说明默认3000上限，当前任务记录费用依据，所有提交和返工计入 |
| 输出是真成片 | 实测媒体、声音与字幕；不把受理状态或透明层当短剧 |

完整对应关系见[用户要求追踪](docs/requirements.md)。

## 必需依赖

来源：[zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills)，MIT。锁定commit与路径见[依赖锁定](skills/xiyou-antifraud-short-drama/references/dependencies.lock.json)。

- `short-drama-write`
- `short-drama-storyboard`
- `short-drama-review`

安装器用Python 3.9+标准库，只下载缺少的技能及许可证，不执行下载代码，不覆盖已有目录。从安装后的本技能文件夹运行：

```bash
python3 scripts/ensure_dependencies.py --check
python3 scripts/ensure_dependencies.py --install
```

其他宿主目录加`--dest /实际技能目录`。详情见[依赖说明](skills/xiyou-antifraud-short-drama/references/dependencies.md)。平台登录、模型使用资格、Image权限和积分需接收方各自具备；依赖安装不替代这些能力。

## 流程

依赖检查与缺项安装 → 权威案例 → 写作Skill与AI审查修订 → 分镜Skill → Image人物／关键帧与AI选片 → 实时报价及累计预算核算 → 即梦分段生成 → 实际看片与局部修复 → 中文排字、字幕、混音 → 媒体验收与最终MP4交付。

全自动默认不需要用户先审剧本或图片。只有用户明确要求“先给剧本审核／暂不生图／只做某阶段”才切换局部输出模式；不把AI自检写成用户已批准。已有任务承接当前进度，不重复生成或重复扣费。价格实时查询，不把上一部报价当现价。

## 目录

```text
skills/xiyou-antifraud-short-drama/
  SKILL.md
  agents/openai.yaml
  references/         # 依赖、叙事节奏、制作预算、审查与提示词
  assets/templates/   # 参数、分段、字幕、画面文字、预算
  scripts/            # 缺项安装器与成片技术验收
```

`examples/`提供可复制启动语；`tests/`验证依赖安装的真实边界。仓库发布原创工作流、模板与辅助代码；媒体示例保留在原制作项目。此仓库不附带平台账号、密钥或商业平台内部创作技能。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 skills/xiyou-antifraud-short-drama/scripts/ensure_dependencies.py --check
# 安装FFmpeg与FFprobe后，可技术检查真实成片：
python3 skills/xiyou-antifraud-short-drama/scripts/verify_video.py /成片路径.mp4
```

技术检查不代替剧情、口型、中文可读性与“有BGM但没有内容”的看片。MP4中的判断按钮只是视觉提示，真正交互游戏另接事件与止损分支。

## 许可证与致谢

本仓库原创工作流、模板与辅助代码采用[MIT](LICENSE)。外部依赖保留各自许可证，参见[第三方说明](THIRD_PARTY_NOTICES.md)。

## v2.0.0

默认执行模式从逐阶段人工审核改为全自动：只需主动调用技能并给诈骗类型，创意阶段由AI审稿、选片与修订，一直推进到实际成片。原有节奏、案例、画风、模型、中文与预算要求保留；明确只做剧本的用户要求仍优先。
