"""
内容预览节点
整合所有生成内容，输出完整的预览信息供用户审核
"""

import json
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import PreviewInput, PreviewOutput


def preview_node(
    state: PreviewInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PreviewOutput:
    """
    title: 内容预览
    desc: 整合标题、正文、标签和配图，生成完整的预览信息和发布建议
    integrations: 无外部集成
    """
    
    # 构建完整的预览信息
    preview_info: Dict[str, Any] = {
        "note_type": state.note_type,
        "title": state.title,
        "content": state.content,
        "tags": state.tags,
        "image_url": state.image_url,
        "content_length": len(state.content),
        "tag_count": len(state.tags),
        "publish_time_suggestion": "建议在早上8-9点或晚上6-7点发布",
        "target_audience": "年轻打工人群体",
        "engagement_prediction": "高" if "收藏" in state.note_type else "中"
    }
    
    # 计算内容质量评分
    quality_score = 0.0
    
    # 标题评分（标题长度适中、吸引眼球）
    if len(state.title) >= 5 and len(state.title) <= 30:
        quality_score += 20
    elif len(state.title) > 0:
        quality_score += 10
    
    # 内容评分（内容长度适中）
    if len(state.content) >= 100 and len(state.content) <= 800:
        quality_score += 30
    elif len(state.content) >= 50:
        quality_score += 20
    
    # 标签评分（标签数量适中）
    if len(state.tags) >= 5 and len(state.tags) <= 10:
        quality_score += 20
    elif len(state.tags) >= 3:
        quality_score += 10
    
    # 配图评分
    if state.image_url and state.image_url.startswith("http"):
        quality_score += 20
    
    # 笔记类型适配评分
    if state.note_type == "收藏型":
        # 收藏型需要实用性强的内容
        if "清单" in state.title or "技巧" in state.title or "指南" in state.title:
            quality_score += 10
    else:
        # 讨论型需要互动性强的问题
        if "?" in state.title or "？" in state.title or "你" in state.title:
            quality_score += 10
    
    # 生成发布建议
    publish_suggestion = ""
    if quality_score >= 80:
        publish_suggestion = "内容质量优秀，建议直接发布。可选择高峰时段（早8-9点或晚6-7点）以获得更高曝光。"
    elif quality_score >= 60:
        publish_suggestion = "内容质量良好，可以发布。建议检查标题是否足够吸引眼球，适当调整标签数量。"
    else:
        publish_suggestion = "内容质量有待提升，建议重新生成或手动优化。注意：标题应简洁有力，内容应控制在合理长度，配图不可缺失。"
    
    preview_info["quality_score"] = quality_score
    preview_info["publish_suggestion"] = publish_suggestion
    
    return PreviewOutput(
        preview_info=preview_info,
        quality_score=quality_score,
        publish_suggestion=publish_suggestion
    )