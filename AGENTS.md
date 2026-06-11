"""
小红书笔记与全天问候自动生成工作流

本项目实现针对年轻打工人的日常养生与成长主题小红书笔记每日自动生成工作流，
同时支持全天候问候推送系统（6个时间点）。

主要功能：
1. 小红书笔记生成
   - 支持两类笔记类型：收藏型（实用清单、干货整理）和讨论型（话题互动、问题征集）
   - 主题方向覆盖：养生打工人、赚钱爱自己、职场成长、生活小技巧
   - 自动生成笔记内容：标题、正文、标签、配图
   - 内容预览与质量评估功能
   - 推送到企业微信

2. 全天候问候推送系统（6个时间点）
   - 早安 (09:30)：温馨早安问候，开启美好一天
   - 午饭 (12:00)：午餐提醒，健康饮食倡导
   - 午休 (12:30)：午间休息提醒，充电小贴士
   - 下午茶 (15:30)：下午茶时光，能量补给
   - 下班 (18:00)：下班问候，犒劳辛苦的自己
   - 晚安 (22:00)：温馨晚安，好好休息
   
   - 每个时间点有5种不同场景，每天随机选择，图片多变不重复
   - 文案模型：doubao-seed-1-8-251228（豆包Seed）
   - 图片模型：doubao-seedream-5-0-260128（SeeDream v5.0）

工作流结构：
入口 → 条件判断(content_type)
  ├→ 笔记内容分支：话题选择 → 内容生成(Agent) → 图片生成 → 推送到企业微信
  └→ 问候推送分支：问候文案生成(Agent) → 图片生成(多场景随机) → 微信推送

使用方式：
- 笔记内容：输入笔记类型、主题方向 → 输出完整笔记内容并推送
- 问候推送：输入greeting_type（早安/午饭/午休/下午茶/下班/晚安）→ 输出问候内容+配图+推送状态

定时调度（cron-job.org外部触发）：
- 早安: 09:30（event_type: morning）
- 午饭: 12:00（event_type: lunch）
- 午休: 12:30（event_type: lunch_rest）
- 下午茶: 15:30（event_type: afternoon）
- 下班: 18:00（event_type: evening）
- 晚安: 22:00（event_type: night）
- GitHub Actions workflow: .github/workflows/daily_greeting.yml
- 推送渠道: 企业微信Webhook

图片生成特点：
- 每个时间点5种场景池，根据日期随机选择
- 去除时钟元素，通过场景氛围体现时间特征
- flat vector illustration, cute kawaii风格
"""

# 节点清单
# | 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
# |-------|---------|------|---------|---------|---------|
# | content_type_check | graph.py | condition | 判断内容类型选择分支 | "问候推送"→greeting_gen, "笔记内容"→topic_select | - |
# | greeting_type_check | graph.py | condition | 判断问候类型 | 6种问候类型各有分支 | - |
# | topic_select | nodes/topic_select_node.py | task | 根据笔记类型和主题选择话题 | - | - |
# | content_gen | nodes/content_gen_node.py | agent | 使用LLM生成笔记内容 | - | config/content_gen_cfg.json |
# | note_image_gen | nodes/note_image_gen_node.py | task | 根据笔记内容生成配图 | - | - |
# | note_push | nodes/note_push_node.py | task | 推送笔记内容到企业微信 | - | - |
# | greeting_gen | nodes/greeting_gen_node.py | agent | 使用LLM生成问候文案 | - | config/greeting_gen_cfg.json |
# | greeting_image_gen | nodes/greeting_image_gen_node.py | task | 生成问候配图(多场景随机) | - | - |
# | wechat_push | nodes/wechat_push_node.py | task | 推送问候内容到企业微信 | - | - |

# 类型说明: task(普通任务节点) / agent(大模型节点) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

# 模型配置
# | 模型用途 | 模型ID | 配置文件 |
# |---------|--------|---------|
# | 文案生成 | doubao-seed-1-8-251228 | config/greeting_gen_cfg.json |
# | 图片生成 | doubao-seedream-5-0-260128 | - |

# 技能使用
# - LLM调用：使用火山引擎方舟API（Ark API）
# - 图片生成：使用ImageGenerationClient（SeeDream v5.0）
# - 企业微信推送：通过Webhook URL