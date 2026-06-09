"""
小红书笔记自动生成工作流

本项目实现针对年轻打工人的日常养生与成长主题小红书笔记每日自动生成工作流，
同时支持每日早安问候推送功能。

主要功能：
1. 小红书笔记生成
   - 支持两类笔记类型：收藏型（实用清单、干货整理）和讨论型（话题互动、问题征集）
   - 主题方向覆盖：养生打工人、赚钱爱自己、职场成长、生活小技巧
   - 自动生成笔记内容：标题、正文、标签、配图
   - 内容预览与质量评估功能

2. 早安问候推送（每天9:30）
   - 每天生成不重复的早安问候文案
   - 风格可定制：温馨治愈、鸡血励志、幽默调侃、随意
   - 自动生成配图
   - 推送到企业微信群提醒

工作流结构：
入口 → 条件判断(content_type)
  ├→ 笔记内容分支：话题选择 → 内容生成(Agent) → 图片生成 → 内容预览
  └→ 早安问候分支：问候文案生成(Agent) → 图片生成 → 微信推送

使用方式：
- 笔记内容：输入笔记类型、主题方向 → 输出完整笔记内容
- 早安问候：输入greeting_style → 输出问候内容+配图+推送状态
"""

# 节点清单
# | 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
# |-------|---------|------|---------|---------|---------|
# | content_type_check | graph.py | condition | 判断内容类型选择分支 | "早安问候"→greeting_gen, "笔记内容"→topic_select | - |
# | topic_select | nodes/topic_select_node.py | task | 根据笔记类型和主题选择话题 | - | - |
# | content_gen | nodes/content_gen_node.py | agent | 使用LLM生成笔记内容 | - | config/content_gen_cfg.json |
# | image_gen | nodes/image_gen_node.py | task | 根据内容生成配图 | - | - |
# | preview | nodes/preview_node.py | task | 整合输出内容预览 | - | - |
# | greeting_gen | nodes/greeting_gen_node.py | agent | 使用LLM生成早安问候文案 | - | config/greeting_gen_cfg.json |
# | greeting_image_gen | nodes/greeting_image_gen_node.py | task | 生成早安问候配图 | - | - |
# | wechat_push | nodes/wechat_push_node.py | task | 推送到企业微信群 | - | - |

# 类型说明: task(普通任务节点) / agent(大模型节点) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

# 子图清单
# 无子图（主图为带条件分支的DAG结构）

# 技能使用
# - content_gen节点使用大语言模型技能(LLMClient)
# - greeting_gen节点使用大语言模型技能(LLMClient)
# - image_gen节点使用图片生成技能(ImageGenerationClient)
# - greeting_image_gen节点使用图片生成技能(ImageGenerationClient)
# - wechat_push节点使用企业微信机器人集成(integration-wechat-bot)

# 集成配置要求
# 企业微信机器人推送需要配置 webhook_key：
# 1. 在企业微信群中添加机器人获取webhook URL
# 2. 在平台上配置 integration-wechat-bot 集成

# 话题库说明（笔记内容分支）
# 预定义话题库位于 topic_select_node.py，包含以下主题方向：
# - 养生打工人：办公室养生、健康早餐、颈椎保健、养生茶、午休指南等
# - 赚钱爱自己：理财入门、副业思路、省钱技巧、升薪建议、省钱APP等
# - 职场成长：新人技能、沟通技巧、办公软件、邮件写作、会议记录等
# - 生活小技巧：独居指南、租房避坑、通勤利用、周末充电、时间管理等

# 早安问候说明
# - 每天生成不重复内容（结合日期、星期变化）
# - 风格可选：温馨治愈/鸡血励志/幽默调侃/随意
# - 段落式内容，适合小红书发布
# - 配图自动生成，温暖治愈风格