"""
问候文案生成节点（Agent节点）
使用大语言模型生成每天不重复的问候文案
支持：早安/午饭/午休/下午茶/下班/晚安 六种类型
"""

import os
import json
from datetime import datetime
from jinja2 import Template
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import GreetingGenInput, GreetingGenOutput, GREETING_TYPE_DESC


# 各类型的文案风格指导
GREETING_TYPE_PROMPT = {
    "早安": {
        "sp": """你是一位温暖有创意的文案创作者，专门为年轻打工人写早安问候。
你的文案风格是：温馨治愈、充满正能量、接地气、有画面感。
每次都要结合当天的情况（日期、天气想象、工作日程等），写出有温度的早安问候。
不要写得太长，控制在150字左右，段落式，适合手机阅读。
多用emoji点缀，比如 ☕ ✨ 🌸 🌞 等。""",
        "up": """今天是 {{today}} {{weekday}}。
请写一段早安问候文案给打工人，风格温馨治愈，内容要：
- 给予鼓励和正能量
- 提醒一些小的行动建议（如喝杯温水、伸展身体）
- 结尾要有温暖的祝福
直接输出文案内容，不要加标题和标签。"""
    },
    "午饭": {
        "sp": """你是一位懂生活的文案创作者，专门为打工人写午餐提醒。
你的文案风格是：接地气、关心健康、美食诱惑、轻松有趣。
提醒打工人好好吃饭，关注营养搭配，不要总是外卖或方便面。
文案控制在100字左右，段落式，多用emoji如 🍜 🥗 🍲 等。""",
        "up": """今天是 {{today}} {{weekday}}，中午12点了。
请写一段午餐提醒文案给打工人，风格轻松有趣，内容要：
- 提醒吃饭时间到了，不要饿着肚子干活
- 给一些简单的午餐建议或健康提醒
- 结尾要有温馨的吃饭祝福
直接输出文案内容。"""
    },
    "午休": {
        "sp": """你是一位关心打工人身心健康的文案创作者，专门写午休提醒。
你的文案风格是：放松舒缓、充电回血、理解打工人的疲惫。
提醒大家短暂休息一下，哪怕闭眼10分钟也是好的。
文案控制在80字左右，段落式，多用emoji如 😴 💤 🛋️ 等。""",
        "up": """今天是 {{today}} {{weekday}}，中午12点半了，午休时间。
请写一段午休提醒文案给打工人，风格舒缓放松，内容要：
- 提醒休息的重要性，哪怕短暂放松也好
- 给一些简单的休息建议（如闭眼、深呼吸）
- 结尾要有温馨的休息祝福
直接输出文案内容。"""
    },
    "下午茶": {
        "sp": """你是一位懂生活的文案创作者，专门为打工人写下午茶提醒。
你的文案风格是：轻松惬意、提神醒脑、小确幸感。
下午三点多容易犯困，提醒大家喝杯茶或咖啡，吃点小零食提神。
文案控制在100字左右，段落式，多用emoji如 🍵 ☕ 🍰 等。""",
        "up": """今天是 {{today}} {{weekday}}，下午3点半了。
请写一段下午茶提醒文案给打工人，风格轻松惬意，内容要：
- 提醒下午茶时间，提神醒脑
- 给一些简单的小建议（如喝咖啡、吃点水果）
- 结尾要有下午加油的祝福
直接输出文案内容。"""
    },
    "下班": {
        "sp": """你是一位懂打工人心声的文案创作者，专门写下班提醒。
你的文案风格是：轻松快乐、犒劳自己、辛苦一天的慰藉。
提醒大家下班了，好好放松，犒劳辛苦一天的自己。
文案控制在100字左右，段落式，多用emoji如 🏠 🌅 🎉 等。""",
        "up": """今天是 {{today}} {{weekday}}，下午6点了，下班时间！
请写一段下班提醒文案给打工人，风格轻松快乐，内容要：
- 庆祝辛苦一天终于结束
- 提醒好好放松，犒劳自己
- 结尾要有温馨的下班祝福
直接输出文案内容。"""
    },
    "晚安": {
        "sp": """你是一位温暖治愈的文案创作者，专门为打工人写晚安问候。
你的文案风格是：安静温柔、抚慰心灵、好好休息。
提醒大家早点休息，明天继续奋斗，晚安好梦。
文案控制在80字左右，段落式，多用emoji如 🌙 ✨ 💫 等。""",
        "up": """今天是 {{today}} {{weekday}}，晚上10点了。
请写一段晚安问候文案给打工人，风格温柔治愈，内容要：
- 提醒早点休息，好好睡眠
- 抚慰一天的疲惫，明天继续加油
- 结尾要有温馨的晚安祝福
直接输出文案内容。"""
    }
}


def greeting_gen_node(
    state: GreetingGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingGenOutput:
    """
    title: 问候文案生成
    desc: 根据问候类型生成每天不重复的问候文案，支持早安/午饭/午休/下午茶/下班/晚安
    integrations: 大语言模型
    """
    
    # 获取问候类型
    greeting_type = state.greeting_type
    
    # 获取当前日期，确保每天内容不同
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%A")
    weekday_cn = {
        "Monday": "周一",
        "Tuesday": "周二",
        "Wednesday": "周三",
        "Thursday": "周四",
        "Friday": "周五",
        "Saturday": "周六",
        "Sunday": "周日"
    }.get(weekday, weekday)
    
    # 获取对应类型的提示词模板
    type_prompt = GREETING_TYPE_PROMPT.get(greeting_type, GREETING_TYPE_PROMPT["早安"])
    sp_content = type_prompt["sp"]
    up_template = type_prompt["up"]
    
    # 从配置文件读取模型配置
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        config.get("configurable", {}).get("llm_cfg", "config/greeting_gen_cfg.json")
    )
    
    llm_config: Dict[str, Any] = {}
    try:
        with open(cfg_file, "r", encoding="utf-8") as fd:
            _cfg = json.load(fd)
            llm_config = _cfg.get("config", {})
    except Exception:
        llm_config = {
            "model": "doubao-seed-1-8-251228",
            "temperature": 0.9,
            "max_completion_tokens": 512
        }
    
    # 使用Jinja2渲染用户提示词
    up_tpl = Template(up_template)
    user_prompt = up_tpl.render({
        "today": today,
        "weekday": weekday_cn,
        "greeting_type": greeting_type
    })
    
    # 创建LLM客户端
    llm_client = LLMClient()
    
    # 构建消息
    messages = [
        SystemMessage(content=sp_content),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型
    response = llm_client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.9),
        max_completion_tokens=llm_config.get("max_completion_tokens", 512),
        top_p=llm_config.get("top_p", 0.95)
    )
    
    # 解析响应内容
    response_content = response.content
    if isinstance(response_content, str):
        content_str = response_content
    elif isinstance(response_content, list):
        text_parts: List[str] = []
        for item in response_content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        content_str = " ".join(text_parts)
    else:
        content_str = str(response_content)
    
    # 清理输出内容
    greeting_content = content_str.strip()
    
    return GreetingGenOutput(
        greeting_content=greeting_content,
        greeting_type=greeting_type
    )