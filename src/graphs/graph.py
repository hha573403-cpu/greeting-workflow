"""
小红书笔记自动生成工作流主图编排
DAG结构：
- 入口 → 条件判断
  ├→ 笔记内容分支：话题选择 -> 内容生成 -> 图片生成 -> 内容预览
  └→ 问候推送分支：问候文案生成 -> 问候图片生成 -> 微信推送
"""

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 导入状态定义
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    TypeCheckInput,
    TopicSelectInput,
    TopicSelectOutput,
    ContentGenInput,
    ContentGenOutput,
    ImageGenInput,
    ImageGenOutput,
    PreviewInput,
    PreviewOutput,
    GreetingGenInput,
    GreetingGenOutput,
    GreetingImageGenInput,
    GreetingImageGenOutput,
    WechatPushInput,
    WechatPushOutput
)

# 导入节点函数
from graphs.nodes.topic_select_node import topic_select_node
from graphs.nodes.content_gen_node import content_gen_node
from graphs.nodes.image_gen_node import image_gen_node
from graphs.nodes.preview_node import preview_node
from graphs.nodes.greeting_gen_node import greeting_gen_node
from graphs.nodes.greeting_image_gen_node import greeting_image_gen_node
from graphs.nodes.wechat_push_node import wechat_push_node


# ==================== 条件判断函数 ====================
def content_type_check(state: GlobalState) -> str:
    """
    title: 内容类型判断
    desc: 根据输入的content_type判断是生成笔记内容还是问候推送，决定后续流程分支
    """
    content_type = state.content_type
    if content_type == "问候推送":
        return "问候推送分支"
    else:
        return "笔记内容分支"


# ==================== 创建状态图 ====================
builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)


# ==================== 添加节点 ====================

# 笔记内容分支节点
builder.add_node("topic_select", topic_select_node)
builder.add_node(
    "content_gen",
    content_gen_node,
    metadata={
        "type": "agent",
        "llm_cfg": "config/content_gen_cfg.json"
    }
)
builder.add_node("image_gen", image_gen_node)
builder.add_node("preview", preview_node)

# 问候推送分支节点
builder.add_node(
    "greeting_gen",
    greeting_gen_node,
    metadata={
        "type": "agent",
        "llm_cfg": "config/greeting_gen_cfg.json"
    }
)
builder.add_node("greeting_image_gen", greeting_image_gen_node)
builder.add_node("wechat_push", wechat_push_node)


# ==================== 设置边 ====================

# 设置入口点为条件判断的起始节点
builder.set_conditional_entry_point(
    path=content_type_check,
    path_map={
        "笔记内容分支": "topic_select",
        "问候推送分支": "greeting_gen"
    }
)

# 笔记内容分支流程
builder.add_edge("topic_select", "content_gen")
builder.add_edge("content_gen", "image_gen")
builder.add_edge("image_gen", "preview")
builder.add_edge("preview", END)

# 问候推送分支流程
builder.add_edge("greeting_gen", "greeting_image_gen")
builder.add_edge("greeting_image_gen", "wechat_push")
builder.add_edge("wechat_push", END)


# ==================== 编译图 ====================
main_graph = builder.compile()