"""
小红书笔记自动生成工作流主图编排
DAG结构：话题选择 -> 内容生成 -> 图片生成 -> 内容预览
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
    TopicSelectInput,
    TopicSelectOutput,
    ContentGenInput,
    ContentGenOutput,
    ImageGenInput,
    ImageGenOutput,
    PreviewInput,
    PreviewOutput
)

# 导入节点函数
from graphs.nodes.topic_select_node import topic_select_node
from graphs.nodes.content_gen_node import content_gen_node
from graphs.nodes.image_gen_node import image_gen_node
from graphs.nodes.preview_node import preview_node


# 创建状态图
builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)

# ==================== 添加节点 ====================

# 话题选择节点（非Agent节点，简单逻辑）
builder.add_node("topic_select", topic_select_node)

# 内容生成节点（Agent节点，使用大语言模型）
builder.add_node(
    "content_gen",
    content_gen_node,
    metadata={
        "type": "agent",
        "llm_cfg": "config/content_gen_cfg.json"
    }
)

# 图片生成节点（非Agent节点，使用多模态模型）
builder.add_node("image_gen", image_gen_node)

# 内容预览节点（非Agent节点，整合输出）
builder.add_node("preview", preview_node)


# ==================== 设置边 ====================

# 设置入口点
builder.set_entry_point("topic_select")

# 话题选择 -> 内容生成
builder.add_edge("topic_select", "content_gen")

# 内容生成 -> 图片生成
builder.add_edge("content_gen", "image_gen")

# 图片生成 -> 内容预览
builder.add_edge("image_gen", "preview")

# 内容预览 -> 结束
builder.add_edge("preview", END)


# ==================== 编译图 ====================
main_graph = builder.compile()