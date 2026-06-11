"""
问候图片生成节点
根据问候类型生成配图
支持：早安/午饭/午休/下午茶/下班/晚安 六种类型
"""

import datetime
import logging
from typing import List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import ImageGenerationClient
from graphs.state import (
    GreetingImageGenInput,
    GreetingImageGenOutput,
    GREETING_TYPE_IMAGE_STYLE
)

logger = logging.getLogger(__name__)


# 各类型的图片提示词模板 - 强调时间特征，一眼看出时间段
GREETING_TYPE_IMAGE_PROMPT = {
    "早安": "flat vector illustration, cute kawaii style, bright morning sunrise with golden sun rays coming through window, alarm clock showing 9:30 AM, steaming coffee cup and toast on breakfast table, warm orange and yellow morning light, fresh flowers in vase, no text, simple clean design, digital art",
    
    "午饭": "flat vector illustration, cute kawaii style, clock showing 12:00 noon, delicious lunch bento box with rice vegetables and fruits on table, chopsticks and spoon, bright midday sunlight from window, warm orange and green colors, no text, simple clean design, digital art",
    
    "午休": "flat vector illustration, cute kawaii style, clock showing 12:30 PM, person resting on office chair with eyes closed, soft pillow and blanket, calm blue and white colors, quiet afternoon atmosphere, window with soft light, no text, simple clean design, digital art",
    
    "下午茶": "flat vector illustration, cute kawaii style, clock showing 3:30 PM, coffee cup with latte art and slice of cake on office desk, warm afternoon sunlight streaming through window, soft pink and beige colors, cozy relaxing vibe, no text, simple clean design, digital art",
    
    "下班": "flat vector illustration, cute kawaii style, clock showing 6:00 PM, beautiful orange and pink sunset sky with sun going down, silhouette of city buildings and office worker walking home, golden evening light, warm orange and gold colors, no text, simple clean design, digital art",
    
    "晚安": "flat vector illustration, cute kawaii style, clock showing 10:00 PM, crescent moon and stars in night sky through bedroom window, soft bedside lamp with warm glow, cozy bed with pillows and blanket, deep blue and purple night colors, peaceful sleeping atmosphere, no text, simple clean design, digital art",
}


def greeting_image_gen_node(
    state: GreetingImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingImageGenOutput:
    """
    title: 问候图片生成
    desc: 根据问候类型生成治愈系配图，使用AI图片生成服务
    integrations: 图片生成
    """
    ctx = runtime.context
    greeting_type = state.greeting_type
    
    # 获取对应类型的图片提示词
    image_prompt = GREETING_TYPE_IMAGE_PROMPT.get(greeting_type, GREETING_TYPE_IMAGE_PROMPT["早安"])
    
    # 获取风格描述（用于日志）
    style_info = GREETING_TYPE_IMAGE_STYLE.get(greeting_type, "治愈系插画")
    logger.info(f"图片风格: {style_info}")
    logger.info(f"图片提示词: {image_prompt}")
    
    # 使用图片生成客户端
    img_client = ImageGenerationClient()
    
    # 获取今天的日期作为seed（保证同一天生成相同风格）
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # 尝试生成AI图片
    image_url = ""
    
    try:
        response = img_client.generate(
            prompt=image_prompt,
            size="2K",
            watermark=False
        )
        
        if response.success and response.data and len(response.data) > 0:
            image_url = response.data[0].url
            logger.info(f"AI图片生成成功: {image_url}")
        else:
            logger.warning(f"AI图片生成失败: {response.message if hasattr(response, 'message') else 'unknown error'}")
    except Exception as e:
        logger.warning(f"图片生成异常: {str(e)}")
    
    # 如果AI生成失败，使用带日期seed的picsum作为备选
    if not image_url:
        image_url = f"https://picsum.photos/seed/{today}/800/600"
        logger.info(f"使用picsum备选图片: {image_url}")
    
    return GreetingImageGenOutput(
        greeting_image_url=image_url,
        image_prompt=image_prompt,
        greeting_type=greeting_type
    )