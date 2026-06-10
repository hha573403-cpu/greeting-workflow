"""
问候图片生成节点
根据问候类型生成配图
支持：早安/午饭/午休/下午茶/下班/晚安 六种类型
"""

import datetime
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


# 各类型的图片提示词模板 - 强调治愈系插画风格
GREETING_TYPE_IMAGE_PROMPT = {
    "早安": """
Create a warm morning illustration for young office workers.

Style: Soft hand-drawn illustration, cozy pastel colors, healing aesthetic, NOT realistic photo.

Scene elements:
- Sunlight streaming through a cozy window with curtains
- A steaming cup of coffee or tea on a wooden desk
- Small potted plants or fresh flowers
- Morning light rays, warm orange-yellow tones
- Minimalist flat illustration style, clean composition
- Gentle brush strokes, dreamy atmosphere
- Perfect for social media sharing
""",
    "午饭": """
Create a cozy lunch illustration for young office workers.

Style: Warm hand-drawn illustration, appetizing food scene, healing aesthetic, NOT realistic photo.

Scene elements:
- A lovely bento box or simple meal on table
- Fresh vegetables, fruits, rice in soft colors
- Warm table setting with simple utensils
- Soft lighting, pleasant dining atmosphere
- Minimalist flat illustration style
- Pastel orange, warm beige, fresh green tones
- Perfect for social media sharing
""",
    "午休": """
Create a relaxing nap time illustration for young office workers.

Style: Peaceful hand-drawn illustration, restful atmosphere, healing aesthetic, NOT realistic photo.

Scene elements:
- A comfortable sofa or lounge chair
- Soft pillows and cozy blanket
- Gentle afternoon light, quiet atmosphere
- Small plants, a book, relaxing elements
- Soft blue, cream white, pale green tones
- Minimalist flat illustration style
- Perfect for social media sharing
""",
    "下午茶": """
Create a pleasant afternoon tea illustration for young office workers.

Style: Cozy hand-drawn illustration, refreshing vibes, healing aesthetic, NOT realistic photo.

Scene elements:
- A cup of coffee or tea with steam
- Cute pastries or fresh fruits beside
- Afternoon sunlight or soft warm lamp
- Cozy desk corner or cafe atmosphere
- Warm but gentle color tones
- Minimalist flat illustration style
- Perfect for social media sharing
""",
    "下班": """
Create a joyful after-work illustration for young office workers.

Style: Warm hand-drawn illustration, sunset vibes, healing aesthetic, NOT realistic photo.

Scene elements:
- Beautiful sunset sky with orange-pink clouds
- City silhouette or peaceful street
- Relaxed, happy atmosphere after work day
- Soft golden-orange, warm pink tones
- Minimalist flat illustration style
- Gentle brush strokes, dreamy feeling
- Perfect for social media sharing
""",
    "晚安": """
Create a peaceful goodnight illustration for young office workers.

Style: Serene hand-drawn illustration, bedtime vibes, healing aesthetic, NOT realistic photo.

Scene elements:
- Night sky with crescent moon and soft stars
- Cozy bedroom window with warm lamp light
- Soft pillows, a book, peaceful elements
- Deep blue, purple, warm yellow accent tones
- Minimalist flat illustration style
- Gentle, dreamy atmosphere
- Perfect for social media sharing
"""
}


def greeting_image_gen_node(
    state: GreetingImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingImageGenOutput:
    """
    title: 问候图片生成
    desc: 根据问候类型生成配图，支持早安/午饭/午休/下午茶/下班/晚安
    integrations: 图片生成模型
    """
    
    greeting_type = state.greeting_type
    greeting_content = state.greeting_content
    
    # 获取对应类型的图片风格和提示词模板
    image_style = GREETING_TYPE_IMAGE_STYLE.get(greeting_type, "温暖治愈的风格")
    image_prompt_template = GREETING_TYPE_IMAGE_PROMPT.get(greeting_type, GREETING_TYPE_IMAGE_PROMPT["早安"])
    
    # 构建完整的图片提示词
    image_prompt = f"""
{image_prompt_template}

Important: This must be a soft hand-drawn illustration style, NOT a realistic photograph.
Use pastel colors, gentle brush strokes, minimalist flat design.
The image should feel warm, healing, and cozy - perfect for young office workers.
"""
    
    # 生成基于日期和类型的seed，确保同一天同一类型返回相同图片
    today = datetime.datetime.now().strftime("%Y%m%d")
    type_seed_map = {
        "早安": "morning",
        "午饭": "lunch",
        "午休": "nap",
        "下午茶": "tea",
        "下班": "offwork",
        "晚安": "night"
    }
    type_seed = type_seed_map.get(greeting_type, "morning")
    
    # 创建图片生成客户端
    img_client = ImageGenerationClient()
    
    # 调用图片生成
    try:
        response = img_client.generate(
            prompt=image_prompt,
            size="2K",
            watermark=False
        )
        
        if response.success and response.image_urls:
            greeting_image_url = response.image_urls[0]
        else:
            # 使用带seed的picsum作为备选，确保同一天同一类型图片一致
            greeting_image_url = f"https://picsum.photos/seed/{today}-{type_seed}/800/600"
    except Exception:
        # 使用带seed的picsum作为备选
        greeting_image_url = f"https://picsum.photos/seed/{today}-{type_seed}/800/600"
    
    return GreetingImageGenOutput(
        greeting_image_url=greeting_image_url,
        greeting_type=greeting_type,
        image_prompt=image_prompt.strip()
    )