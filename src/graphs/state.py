"""
小红书笔记自动生成工作流状态定义
目标受众：年轻打工人
笔记类型：收藏型、讨论型
主题方向：养生打工人、赚钱爱自己等积极情绪内容
一日问候功能：早安/午饭/午休/下午茶/下班/晚安，全天候陪伴
"""

from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from utils.file.file import File


# ==================== 问候类型常量 ====================
GREETING_TYPES = Literal["早安", "午饭", "午休", "下午茶", "下班", "晚安"]

# 各类型的主题描述
GREETING_TYPE_DESC = {
    "早安": "元气满满的一天开始，给打工人加油鼓劲",
    "午饭": "吃饭时间提醒，营养健康小贴士",
    "午休": "休息充电，下午更有精力",
    "下午茶": "提神醒脑，下午继续加油",
    "下班": "辛苦一天，犒劳自己",
    "晚安": "好好休息，明天继续奋斗"
}

# 各类型的图片风格
GREETING_TYPE_IMAGE_STYLE = {
    "早安": "温暖明亮的早晨色调，阳光、咖啡、窗边，充满希望和能量",
    "午饭": "美食相关，温馨的餐桌氛围，健康营养的感觉",
    "午休": "安静放松的氛围，舒适的休息场景，充电回血的感觉",
    "下午茶": "轻松惬意，咖啡茶点，下午时光，提神醒脑",
    "下班": "轻松快乐的氛围，夕阳、回家路上的温馨感，犒劳自己",
    "晚安": "温馨宁静的夜晚氛围，月亮星星，舒适放松的感觉"
}


# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """工作流全局状态"""
    # 通用字段
    content_type: str = Field(default="问候推送", description="内容类型：笔记内容或问候推送")
    
    # 笔记内容相关
    note_type: str = Field(default="收藏型", description="笔记类型：收藏型或讨论型")
    theme_direction: str = Field(default="养生打工人", description="主题方向：养生打工人、赚钱爱自己等")
    selected_topic: str = Field(default="", description="选中的具体话题")
    title: str = Field(default="", description="笔记标题")
    content: str = Field(default="", description="笔记正文内容")
    tags: List[str] = Field(default=[], description="笔记标签列表")
    image_url: str = Field(default="", description="配图URL")
    preview_info: Dict[str, Any] = Field(default={}, description="完整预览信息")
    
    # 问候推送相关
    greeting_type: str = Field(default="早安", description="问候类型：早安/午饭/午休/下午茶/下班/晚安")
    greeting_content: str = Field(default="", description="问候文案内容")
    greeting_image_url: str = Field(default="", description="问候配图URL")
    
    push_status: str = Field(default="", description="推送状态：成功/失败")


# ==================== 工作流输入输出 ====================
class GraphInput(BaseModel):
    """工作流输入"""
    content_type: Literal["笔记内容", "问候推送"] = Field(
        default="问候推送",
        description="内容类型：笔记内容（生成小红书笔记）或问候推送（生成每日问候推送）"
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
    # 问候推送参数
    greeting_type: Literal["早安", "午饭", "午休", "下午茶", "下班", "晚安"] = Field(
        default="早安",
        description="问候类型：早安(9:30)/午饭(12:00)/午休(12:30)/下午茶(15:30)/下班(18:00)/晚安(22:00)"
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
    
    # 问候推送输出（当content_type=问候推送时）
    greeting_type: str = Field(default="", description="问候类型")
    greeting_content: str = Field(default="", description="问候文案")
    greeting_image_url: str = Field(default="", description="问候配图URL")
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


# ==================== 问候生成节点定义 ====================

# 问候文案生成节点
class GreetingGenInput(BaseModel):
    """问候文案生成节点输入"""
    greeting_type: str = Field(..., description="问候类型：早安/午饭/午休/下午茶/下班/晚安")


class GreetingGenOutput(BaseModel):
    """问候文案生成节点输出"""
    greeting_content: str = Field(..., description="问候文案（段落式，适合推送）")
    greeting_type: str = Field(..., description="问候类型")


# 问候图片生成节点
class GreetingImageGenInput(BaseModel):
    """问候图片生成节点输入"""
    greeting_content: str = Field(..., description="问候文案")
    greeting_type: str = Field(..., description="问候类型")


class GreetingImageGenOutput(BaseModel):
    """问候图片生成节点输出"""
    greeting_image_url: str = Field(..., description="问候配图URL")
    greeting_type: str = Field(..., description="问候类型（从输入传递）")
    image_prompt: str = Field(default="", description="生成图片的提示词")


# 微信推送节点
class WechatPushInput(BaseModel):
    """微信推送节点输入"""
    greeting_type: str = Field(..., description="问候类型")
    greeting_content: str = Field(..., description="问候文案")
    greeting_image_url: str = Field(default="", description="问候配图URL")


class WechatPushOutput(BaseModel):
    """微信推送节点输出"""
    push_status: str = Field(..., description="推送状态：成功/失败")
    push_message: str = Field(default="", description="推送结果信息")


# 笔记内容推送节点
class NotePushInput(BaseModel):
    """笔记内容推送节点输入"""
    note_type: str = Field(..., description="笔记类型：收藏型/讨论型")
    theme_direction: str = Field(..., description="主题方向")
    title: str = Field(..., description="笔记标题")
    content: str = Field(..., description="笔记正文")
    tags: List[str] = Field(default=[], description="笔记标签列表")
    image_url: str = Field(default="", description="配图URL")


class NotePushOutput(BaseModel):
    """笔记内容推送节点输出"""
    push_status: str = Field(..., description="推送状态：成功/失败")
    push_message: str = Field(default="", description="推送结果信息")