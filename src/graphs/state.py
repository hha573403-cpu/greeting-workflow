"""
小红书笔记自动生成工作流状态定义
目标受众：年轻打工人
笔记类型：收藏型、讨论型
主题方向：养生打工人、赚钱爱自己等积极情绪内容
新增功能：早安问候（每天9:30推送，每天不重复）
"""

from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """工作流全局状态"""
    # 通用字段
    content_type: str = Field(default="笔记内容", description="内容类型：笔记内容或早安问候")
    
    # 笔记内容相关
    note_type: str = Field(default="收藏型", description="笔记类型：收藏型或讨论型")
    theme_direction: str = Field(default="养生打工人", description="主题方向：养生打工人、赚钱爱自己等")
    selected_topic: str = Field(default="", description="选中的具体话题")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文内容")
    tags: List[str] = Field(default=[], description="笔记标签列表")
    image_url: str = Field(default="", description="配图URL")
    preview_info: Dict[str, Any] = Field(default={}, description="完整预览信息")
    
    # 早安问候相关
    greeting_content: str = Field(default="", description="早安问候文案内容")
    greeting_image_url: str = Field(default="", description="早安问候配图URL")
    greeting_style: str = Field(default="随意", description="问候风格：温馨治愈/鸡血励志/幽默调侃/随意")
    push_status: str = Field(default="", description="推送状态：成功/失败")


# ==================== 工作流输入输出 ====================
class GraphInput(BaseModel):
    """工作流输入"""
    content_type: Literal["笔记内容", "早安问候"] = Field(
        default="笔记内容",
        description="内容类型：笔记内容（生成小红书笔记）或早安问候（生成每日早安推送）"
    )
    # 笔记内容参数
    note_type: Literal["收藏型", "讨论型"] = Field(
        default="收藏型",
        description="笔记类型：收藏型（实用清单、干货整理）或讨论型（话题互动、问题征集）"
    )
    theme_direction: str = Field(
        default="养生打工人",
        description="主题方向：养生打工人、赚钱爱自己、职场成长、生活小技巧等"
    )
    # 早安问候参数
    greeting_style: Literal["温馨治愈", "鸡血励志", "幽默调侃", "随意"] = Field(
        default="随意",
        description="早安问候风格"
    )


class GraphOutput(BaseModel):
    """工作流输出"""
    content_type: str = Field(..., description="内容类型")
    
    # 笔记内容输出（当content_type=笔记内容时）
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文内容")
    tags: List[str] = Field(default=[], description="笔记标签列表")
    image_url: str = Field(default="", description="配图URL")
    preview_info: Dict[str, Any] = Field(default={}, description="完整预览信息")
    
    # 早安问候输出（当content_type=早安问候时）
    greeting_content: str = Field(default="", description="早安问候文案")
    greeting_image_url: str = Field(default="", description="早安问候配图URL")
    push_status: str = Field(default="", description="推送状态")


# ==================== 节点输入输出定义 ====================

# 类型判断节点
class TypeCheckInput(BaseModel):
    """类型判断节点输入"""
    content_type: str = Field(..., description="内容类型")


class TypeCheckOutput(BaseModel):
    """类型判断节点输出（条件节点不需要Output，直接返回分支名）"""
    pass


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


# 图片生成节点（笔记）
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


# ==================== 早安问候节点定义 ====================

# 早安文案生成节点
class GreetingGenInput(BaseModel):
    """早安文案生成节点输入"""
    greeting_style: str = Field(default="随意", description="问候风格")


class GreetingGenOutput(BaseModel):
    """早安文案生成节点输出"""
    greeting_content: str = Field(..., description="早安问候文案（段落式，适合小红书）")
    greeting_title: str = Field(default="", description="早安问候标题")


# 早安图片生成节点
class GreetingImageGenInput(BaseModel):
    """早安图片生成节点输入"""
    greeting_content: str = Field(..., description="早安问候文案")
    greeting_style: str = Field(default="随意", description="问候风格")


class GreetingImageGenOutput(BaseModel):
    """早安图片生成节点输出"""
    greeting_image_url: str = Field(..., description="早安问候配图URL")
    image_prompt: str = Field(default="", description="生成图片的提示词")


# 微信推送节点
class WechatPushInput(BaseModel):
    """微信推送节点输入"""
    greeting_content: str = Field(..., description="早安问候文案")
    greeting_image_url: str = Field(..., description="早安问候配图URL")
    greeting_style: str = Field(default="随意", description="问候风格")


class WechatPushOutput(BaseModel):
    """微信推送节点输出"""
    push_status: str = Field(..., description="推送状态：成功/失败")
    push_message: str = Field(default="", description="推送结果信息")