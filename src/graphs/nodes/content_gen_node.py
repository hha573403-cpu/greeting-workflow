"""
内容生成节点（Agent节点）
使用大语言模型生成小红书笔记内容
"""

import os
import json
from jinja2 import Template
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import ContentGenInput, ContentGenOutput


def content_gen_node(
    state: ContentGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ContentGenOutput:
    """
    title: 内容生成
    desc: 使用大语言模型根据话题生成小红书笔记内容，包括标题、正文和标签
    integrations: 大语言模型
    """
    
    # 从配置文件读取模型配置
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        config.get("configurable", {}).get("llm_cfg", "config/content_gen_cfg.json")
    )
    
    try:
        with open(cfg_file, "r", encoding="utf-8") as fd:
            _cfg = json.load(fd)
    except Exception:
        # 使用默认配置
        _cfg = {
            "config": {
                "model": "doubao-seed-1-8-251228",
                "temperature": 0.8,
                "max_completion_tokens": 2048
            },
            "sp": "你是一位专业的小红书内容创作者，擅长创作吸引年轻打工人的内容。",
            "up": "请根据以下话题创作小红书笔记内容。"
        }
    
    llm_config = _cfg.get("config", {})
    sp_content = _cfg.get("sp", "")
    up_template = _cfg.get("up", "")
    
    # 使用Jinja2渲染用户提示词
    up_tpl = Template(up_template)
    user_prompt = up_tpl.render({
        "topic": state.selected_topic,
        "note_type": state.note_type,
        "theme": state.theme_direction
    })
    
    # 创建LLM客户端（不传ctx参数，因为Context没有logger属性）
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
        temperature=llm_config.get("temperature", 0.8),
        max_completion_tokens=llm_config.get("max_completion_tokens", 2048),
        top_p=llm_config.get("top_p", 0.95)
    )
    
    # 解析响应内容
    response_content = response.content
    if isinstance(response_content, str):
        content_str = response_content
    elif isinstance(response_content, list):
        # 处理列表类型的响应
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
        # 尝试提取JSON部分
        if "{" in content_str and "}" in content_str:
            json_start = content_str.find("{")
            json_end = content_str.rfind("}") + 1
            json_str = content_str[json_start:json_end]
            result = json.loads(json_str)
    except json.JSONDecodeError:
        result = {
            "title": state.selected_topic,
            "content": content_str,
            "tags": ["打工人", "职场", "养生"]
        }
    
    # 提取各字段
    title = result.get("title", state.selected_topic)
    content = result.get("content", content_str)
    tags = result.get("tags", ["打工人", "职场", "养生"])
    content_summary = result.get("summary", "")
    
    # 确保tags是列表
    if not isinstance(tags, list):
        tags = [str(tags)]
    
    return ContentGenOutput(
        title=title,
        content=content,
        tags=tags,
        content_summary=content_summary
    )