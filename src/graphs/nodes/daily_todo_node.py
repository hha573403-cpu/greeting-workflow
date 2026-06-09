"""
每日待办生成节点 - 为打工人生成每日待办提醒
每天生成不重复的待办内容，结合日期、天气、节气变化
"""
import os
import json
import datetime
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from coze_coding_dev_sdk import LLMClient

from graphs.state import DailyTodoInput, DailyTodoOutput


def daily_todo_node(
    state: DailyTodoInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DailyTodoOutput:
    """
    title: 每日待办生成
    desc: 为打工人生成每天不重复的待办提醒内容，结合日期变化
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取LLM配置
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"),
        config.get("metadata", {}).get("llm_cfg", "config/daily_todo_cfg.json")
    )
    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    llm_config = cfg.get("config", {})
    sp = cfg.get("sp", "")
    up = cfg.get("up", "")
    
    # 获取当前日期信息
    today = datetime.datetime.now()
    date_info = {
        "year": today.year,
        "month": today.month,
        "day": today.day,
        "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()],
        "is_weekend": today.weekday() >= 5,
        "season": _get_season(today.month),
        "date_str": today.strftime("%Y年%m月%d日")
    }
    
    # 渲染用户提示词
    up_template = Template(up)
    user_prompt = up_template.render(date_info)
    
    # 初始化LLM客户端
    client = LLMClient()
    
    # 构建消息（使用LangChain消息格式）
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用LLM生成待办内容
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-2-0-lite-260215"),
        temperature=llm_config.get("temperature", 0.8),
        max_completion_tokens=llm_config.get("max_completion_tokens", 500)
    )
    
    # 处理响应内容
    if isinstance(response.content, str):
        todo_content = response.content.strip()
    elif isinstance(response.content, list):
        # 如果是列表格式，提取文本部分
        text_parts = []
        for item in response.content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        todo_content = " ".join(text_parts).strip()
    else:
        todo_content = str(response.content).strip()
    
    return DailyTodoOutput(
        daily_todo_content=todo_content
    )


def _get_season(month: int) -> str:
    """根据月份判断季节"""
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"