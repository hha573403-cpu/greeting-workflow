"""
早安图片生成节点
根据早安问候内容生成配图
"""

import os
import time
import requests
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import ImageGenerationClient
from coze_coding_dev_sdk.s3 import S3SyncStorage
from graphs.state import GreetingImageGenInput, GreetingImageGenOutput


def greeting_image_gen_node(
    state: GreetingImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingImageGenOutput:
    """
    title: 早安图片生成
    desc: 根据早安问候内容和风格生成温馨治愈的配图，上传到对象存储获得固定URL
    integrations: 图片生成模型, 对象存储
    """
    
    # 构建图片生成提示词
    greeting_content = state.greeting_content
    greeting_style = state.greeting_style
    
    # 根据风格调整图片描述
    style_desc = {
        "温馨治愈": "温暖柔和的色调，阳光透过窗户，舒适的氛围，治愈感",
        "鸡血励志": "明亮积极的色调，充满能量感，阳光明媚，振奋人心",
        "幽默调侃": "轻松有趣的插画风格，可爱的元素，活泼的色彩",
        "随意": "自然温暖的风格，清新的色调，舒适的氛围"
    }.get(greeting_style, "温暖治愈的风格")
    
    image_prompt = f"""
创建一张早安问候配图，适合小红书发布。

内容主题：{greeting_content[:100]}
风格要求：{style_desc}

设计元素：
- 温暖明亮的色调，给人积极正能量的感觉
- 适合年轻打工人群体的审美
- 可以包含简约的插画元素、阳光、咖啡杯、书本等日常温馨元素
- 图片要有治愈感，传递"新的一天加油"的积极情绪
- 适合作为小红书早安问候封面展示
"""
    
    # 初始化对象存储客户端
    storage = S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )
    
    # 源图片URL（优先AI生成，备选picsum）
    source_image_url = ""
    
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
            source_image_url = response.image_urls[0]
        else:
            # 使用备用默认图片
            source_image_url = "https://picsum.photos/800/600"
    except Exception:
        source_image_url = "https://picsum.photos/800/600"
    
    # 将图片上传到对象存储，获得固定URL
    try:
        # 从源URL下载图片
        img_response = requests.get(source_image_url, timeout=30)
        img_response.raise_for_status()
        
        # 上传到对象存储
        file_name = f"greeting-images/greeting_{int(time.time())}.jpg"
        file_key = storage.upload_file(
            file_content=img_response.content,
            file_name=file_name,
            content_type="image/jpeg",
        )
        
        # 生成签名URL（24小时有效）
        greeting_image_url = storage.generate_presigned_url(
            key=file_key,
            expire_time=86400,
        )
    except Exception:
        # 如果上传失败，直接使用源URL（但picsum每次访问会变化）
        greeting_image_url = source_image_url
    
    return GreetingImageGenOutput(
        greeting_image_url=greeting_image_url,
        image_prompt=image_prompt.strip()
    )