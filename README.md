# 西游反诈竖屏短剧 Skill

把一个新的真实诈骗类型，做成与《三打白骨精：她还欠俺钱！》同系列的西游反诈短剧。默认54秒、55秒硬上限、9:16、720P、国风少年漫；Image生图，Seedance 2.0 Fast VIP生成视频，中文聊天窗与字幕后期排版。

**这是可安装的Agent Skill，不是只给一份流程说明。** 必须调用剧本、分镜与审查技能；缺少时从锁定的公开上游自动下载缺项，再读取使用。先交剧本审核，授权后才制作媒体。

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
使用 $xiyou-antifraud-short-drama，
把“冒充熟人借钱”的权威公开案例改编成西游反诈短剧。
请先检查并安装缺少的剧本、分镜与审查技能，读取后使用。
保留国风少年漫、55秒以内、9:16、720P。
节奏要快：同一时长增加内容容量，人物紧接上句，压缩无意义空档，
保留必要前情、真实取信过程和剧情反转。
先交完整剧本给我审核，暂不生图或生成视频。
```

只填诈骗类型也能开始。案例和西游桥段未指定时由AI先查证、选择；不会把所有骗局套成返利骗局。

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
| 双阶段审核 | 剧本先审；人物／关键帧及视频报价再确认 |
| 授权后持续制作 | 已授权范围内完成生成、检查、返工、合成与交付 |
| 积分可追踪 | 默认拟定3000上限，实际授权后执行，所有提交和返工计入 |
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

权威案例 → 写作Skill与审查Skill → **剧本审核** → 分镜Skill → Image人物／关键帧 → **素材与视频预算确认** → 即梦分段生成 → 实际看片与局部修复 → 中文排字、字幕、混音 → 媒体验收与交付。

默认从剧本开始；用户已有明确审核与授权时承接进度，不重复询问。默认3000只是拟定上限，不是他人账号的自动付费授权。价格实时查询；不把上一部报价当成现价。

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
