"""
小红书笔记自动生成工作流状态定义
目标受众：年轻打工人
笔记类型：收藏型、讨论型
主题方向：养生打工人、赚钱爱自己等积极情绪内容
"""

from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """工作流全局状态"""
    note_type: str = Field(default="收藏型", description="笔记类型：收藏型或讨论型")
    theme_direction: str = Field(default="养生打工人", description="主题方向：养生打工人、赚钱爱自己等")
    selected_topic: str = Field(default="", description="选中的具体话题")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文内容")
    tags: List[str] = Field(default=[], description="笔记标签列表")
    image_url: str = Field(default="", description="配图URL")
    preview_info: Dict[str, Any] = Field(default={}, description="完整预览信息")


# ==================== 工作流输入输出 ====================
class GraphInput(BaseModel):
    """工作流输入"""
    note_type: Literal["收藏型", "讨论型"] = Field(
        default="收藏型",
        description="笔记类型：收藏型（实用清单、干货整理）或讨论型（话题互动、问题征集）"
    )
    theme_direction: str = Field(
        default="养生打工人",
        description="主题方向：养生打工人、赚钱爱自己、职场成长、生活小技巧等"
    )


class GraphOutput(BaseModel):
    """工作流输出"""
    title: str = Field(..., description="笔记标题")
    content: str = Field(..., description="笔记正文内容")
    tags: List[str] = Field(..., description="笔记标签列表")
    image_url: str = Field(..., description="配图URL")
    preview_info: Dict[str, Any] = Field(..., description="完整预览信息（包含发布建议）")


# ==================== 节点输入输出定义 ====================

# 话题选择节点
class TopicSelectInput(BaseModel):
    """话题选择节点输入"""
    note_type: str = Field(..., description="笔记类型：收藏型或讨论型")
    theme_direction: str = Field(..., description="主题方向")


class TopicSelectOutput(BaseModel):
    """话题选择节点输出"""
    selected_topic: str = Field(..., description="选中的具体话题")
    topic_description: str = Field(default="", description="话题详细描述")


# 内容生成节点
class ContentGenInput(BaseModel):
    """内容生成节点输入"""
    selected_topic: str = Field(..., description="选中的话题")
    note_type: str = Field(..., description="笔记类型")
    theme_direction: str = Field(..., description="主题方向")


class ContentGenOutput(BaseModel):
    """内容生成节点输出"""
    title: str = Field(..., description="笔记标题（吸引眼球）")
    content: str = Field(..., description="笔记正文内容")
    tags: List[str] = Field(..., description="标签列表（5-10个）")
    content_summary: str = Field(default="", description="内容摘要")


# 图片生成节点
class ImageGenInput(BaseModel):
    """图片生成节点输入"""
    title: str = Field(..., description="笔记标题")
    content: str = Field(..., description="笔记正文内容")


class ImageGenOutput(BaseModel):
    """图片生成节点输出"""
    image_url: str = Field(..., description="生成的配图URL")
    image_prompt: str = Field(default="", description="生成图片的提示词")


# 内容预览节点
class PreviewInput(BaseModel):
    """内容预览节点输入"""
    title: str = Field(..., description="笔记标题")
    content: str = Field(..., description="笔记正文")
    tags: List[str] = Field(..., description="标签列表")
    image_url: str = Field(..., description="配图URL")
    note_type: str = Field(..., description="笔记类型")


class PreviewOutput(BaseModel):
    """内容预览节点输出"""
    preview_info: Dict[str, Any] = Field(..., description="完整预览信息")
    quality_score: float = Field(default=0.0, description="内容质量评分（0-100）")
    publish_suggestion: str = Field(default="", description="发布建议")