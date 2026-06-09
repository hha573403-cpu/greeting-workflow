"""
早安文案生成节点（Agent节点）
使用大语言模型生成每天不重复的早安问候文案
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
from graphs.state import GreetingGenInput, GreetingGenOutput


def greeting_gen_node(
    state: GreetingGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingGenOutput:
    """
    title: 早安文案生成
    desc: 使用大语言模型生成每天不重复的早安问候文案，风格可定制，段落式适合小红书发布
    integrations: 大语言模型
    """
    
    # 从配置文件读取模型配置
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        config.get("configurable", {}).get("llm_cfg", "config/greeting_gen_cfg.json")
    )
    
    try:
        with open(cfg_file, "r", encoding="utf-8") as fd:
            _cfg = json.load(fd)
    except Exception:
        # 使用默认配置
        _cfg = {
            "config": {
                "model": "doubao-seed-1-8-251228",
                "temperature": 0.9,
                "max_completion_tokens": 1024
            },
            "sp": "你是一位温暖有创意的文案创作者，专门为打工人写早安问候。",
            "up": "请写一段早安问候文案。"
        }
    
    llm_config = _cfg.get("config", {})
    sp_content = _cfg.get("sp", "")
    up_template = _cfg.get("up", "")
    
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
    
    # 使用Jinja2渲染用户提示词
    up_tpl = Template(up_template)
    user_prompt = up_tpl.render({
        "today": today,
        "weekday": weekday_cn,
        "style": state.greeting_style
    })
    
    # 创建LLM客户端
    llm_client = LLMClient()
    
    # 构建消息
    messages = [
        SystemMessage(content=sp_content),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型（高temperature确保创意性和不重复）
    response = llm_client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.9),
        max_completion_tokens=llm_config.get("max_completion_tokens", 1024),
        top_p=llm_config.get("top_p", 0.95)
    )
    
    # 解析响应内容
    response_content = response.content
    if isinstance(response_content, str):
        content_str = response_content
    elif isinstance(response_content, list):
        text_parts = []
        for item in response_content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        content_str = " ".join(text_parts)
    else:
        content_str = str(response_content)
    
    # 尝试解析JSON格式的输出
    result: Dict[str, Any] = {}
    try:
        if "{" in content_str and "}" in content_str:
            json_start = content_str.find("{")
            json_end = content_str.rfind("}") + 1
            json_str = content_str[json_start:json_end]
            result = json.loads(json_str)
    except json.JSONDecodeError:
        result = {
            "greeting_content": content_str,
            "greeting_title": "早安，打工人！"
        }
    
    greeting_content = result.get("greeting_content", content_str)
    greeting_title = result.get("greeting_title", "早安，打工人！")
    
    return GreetingGenOutput(
        greeting_content=greeting_content,
        greeting_title=greeting_title
    )