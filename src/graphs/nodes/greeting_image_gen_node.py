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


# 各类型的图片提示词模板 - 治愈系插画风格，符合小红书审美
GREETING_TYPE_IMAGE_PROMPT = {
    "早安": """
A warm and energetic morning illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, cozy and healing aesthetic
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Warm pastel color palette: soft orange, cream white, gentle yellow

Scene description:
- Golden morning sunlight streaming through a cozy window
- A steaming cup of coffee or warm tea on a wooden desk
- Small succulent plant or fresh flowers nearby
- Soft light rays creating a hopeful, fresh start feeling
- Clean composition, perfect for social media sharing
- The atmosphere should feel like "a beautiful new day begins"
""",
    "午饭": """
A cozy and appetizing lunch scene illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, warm and inviting
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Warm pastel color palette: soft orange, fresh green, warm beige

Scene description:
- A lovely homemade bento box or simple healthy meal
- Fresh vegetables, fruits, and rice arranged beautifully
- Warm table setting with simple elegant utensils
- Soft natural lighting, pleasant dining atmosphere
- Small decorative elements like a napkin or small plant
- The atmosphere should feel like "enjoy your meal, take care of yourself"
""",
    "午休": """
A peaceful and relaxing nap time illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, serene and calming
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Cool pastel color palette: soft blue, cream white, pale green

Scene description:
- A comfortable lounge chair or soft sofa corner
- Fluffy pillows and a cozy light blanket
- Gentle afternoon light filtering through curtains
- A small book, headphones, or eye mask nearby
- Quiet, restful atmosphere with soft shadows
- The atmosphere should feel like "time to recharge and rest"
""",
    "下午茶": """
A refreshing and delightful afternoon tea illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, cozy and uplifting
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Warm pastel color palette: soft pink, warm beige, gentle brown

Scene description:
- A beautiful cup of coffee or tea with gentle steam
- Cute pastries, cookies, or fresh fruits beside the drink
- Soft afternoon sunlight or warm lamp lighting
- A cozy desk corner or mini cafe atmosphere
- Small decorative touches like a napkin or tiny flowers
- The atmosphere should feel like "a sweet break to brighten your day"
""",
    "下班": """
A joyful and liberating after-work illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, warm and celebratory
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Warm sunset color palette: soft orange, warm pink, golden yellow

Scene description:
- Beautiful sunset sky with soft orange-pink clouds
- City skyline silhouette in gentle outline
- A relaxed figure walking home or peaceful street scene
- Warm golden light creating a "freedom" feeling
- Maybe a small bag, comfortable shoes, happy vibes
- The atmosphere should feel like "work is done, time for yourself"
""",
    "晚安": """
A peaceful and dreamy goodnight illustration for young office workers.

Style requirements:
- Soft hand-drawn illustration style, serene and sleepy
- NOT a realistic photograph - must be illustrated art
- Minimalist flat design with gentle brush strokes
- Cool night color palette: deep blue, soft purple, warm yellow accent

Scene description:
- Night sky with crescent moon and twinkling stars
- A cozy bedroom window with warm soft lamp light inside
- Fluffy pillows, a soft blanket, maybe a book nearby
- Gentle night atmosphere, quiet and peaceful
- Small dreamy elements like floating clouds or moonlight
- The atmosphere should feel like "rest well, tomorrow is a new day"
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

CRITICAL REQUIREMENTS:
- This MUST be a soft hand-drawn illustration, NOT a realistic photograph
- Use pastel colors, gentle gradients, minimal details
- Style: cozy, healing, warm - like a comforting greeting card
- Perfect for young office workers on social media
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