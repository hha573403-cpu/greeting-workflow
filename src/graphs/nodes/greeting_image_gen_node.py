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


# 各类型的图片提示词模板
GREETING_TYPE_IMAGE_PROMPT = {
    "早安": """
创建一张早安问候配图，适合年轻打工人。

风格要求：温暖明亮的早晨色调，阳光、咖啡、窗边，充满希望和能量。

设计元素：
- 温暖的阳光透过窗户或窗帘
- 一杯咖啡或茶，蒸汽袅袅
- 绿植或小花点缀
- 舒适的书桌或窗台场景
- 色调偏暖色系（橙、黄、浅棕）
- 给人新的一天开始的希望感
""",
    "午饭": """
创建一张午餐提醒配图，适合年轻打工人。

风格要求：美食相关，温馨的餐桌氛围，健康营养的感觉。

设计元素：
- 简洁温馨的餐桌或便当
- 健康的食物元素（蔬菜、水果、米饭）
- 温暖的色调，食欲感
- 可以有简单的餐具点缀
- 适合中午提醒的氛围
""",
    "午休": """
创建一张午休提醒配图，适合年轻打工人。

风格要求：安静放松的氛围，舒适的休息场景，充电回血的感觉。

设计元素：
- 舒适的沙发或躺椅
- 柔和的光线，安静的氛围
- 可以有绿植、书籍等放松元素
- 色调偏柔和（浅蓝、米白、淡绿）
- 给人休息放松的感觉
""",
    "下午茶": """
创建一张下午茶提醒配图，适合年轻打工人。

风格要求：轻松惬意，咖啡茶点，下午时光，提神醒脑。

设计元素：
- 一杯咖啡或茶
- 小点心或水果
- 下午的阳光或柔和灯光
- 舒适的办公桌或咖啡厅角落
- 色调偏暖但不过于强烈
- 给人提神醒脑的感觉
""",
    "下班": """
创建一张下班提醒配图，适合年轻打工人。

风格要求：轻松快乐的氛围，夕阳、回家路上的温馨感，犒劳自己。

设计元素：
- 傍晚的夕阳或黄昏天空
- 城市街景或回家的路
- 舒适放松的氛围
- 可以有购物袋、美食元素
- 色调偏暖黄、橙红
- 给人辛苦一天终于结束的解脱感
""",
    "晚安": """
创建一张晚安问候配图，适合年轻打工人。

风格要求：温馨宁静的夜晚氛围，月亮星星，舒适放松的感觉。

设计元素：
- 夜空的月亮和星星
- 温馨的卧室或窗边
- 柔和的灯光
- 可以有书本、枕头等休息元素
- 色调偏深蓝、紫、暖黄点缀
- 给人好好休息、晚安好梦的感觉
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

参考文案主题：{greeting_content[:50] if greeting_content else ''}

要求：高质量、适合小红书发布、温暖治愈感、年轻打工人审美。
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