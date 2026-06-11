"""
图片生成节点
根据笔记内容生成配图
"""

import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import ImageGenerationClient
from graphs.state import ImageGenInput, ImageGenOutput

logger = logging.getLogger(__name__)


def image_gen_node(
    state: ImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ImageGenOutput:
    """
    title: 配图生成
    desc: 根据笔记标题和内容生成符合小红书风格的配图
    integrations: 图片生成模型
    """
    
    # 构建图片生成提示词
    # 结合标题和内容摘要，生成适合小红书的图片描述
    title = state.title
    content_summary = state.content[:200] if len(state.content) > 200 else state.content
    
    # 根据标题关键词生成图片风格描述
    image_prompt = f"""
创建一张温馨、积极向上的小红书风格配图。
主题：{title}
内容背景：{content_summary}

风格要求：
- 色调温暖明亮，给人积极正能量的感觉
- 适合年轻打工人群体的审美
- 可以包含简约的插画元素、温暖的色调、舒适的氛围
- 图片要有治愈感，传递积极情绪
- 尺寸比例适合小红书封面展示
"""
    
    logger.info(f"图片提示词: {image_prompt}")
    
    # 使用图片生成客户端（默认配置，使用integration.coze.cn）
    img_client = ImageGenerationClient()
    logger.info(f"图片生成客户端 base_url: {img_client.config.base_url}")
    
    # 调用图片生成
    try:
        response = img_client.generate(
            prompt=image_prompt,
            size="2K",
            watermark=False
        )
        
        if response.success and response.image_urls:
            image_url = response.image_urls[0]
        else:
            # 使用备用默认图片
            image_url = "https://picsum.photos/800/600"
    except Exception:
        image_url = "https://picsum.photos/800/600"
    
    return ImageGenOutput(
        image_url=image_url,
        image_prompt=image_prompt.strip()
    )