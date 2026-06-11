"""
问候图片生成节点
根据问候类型生成配图
支持：早安/午饭/午休/下午茶/下班/晚安 六种类型
每天生成不同的图片，不重复
"""

import datetime
import logging
import random
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


# 各类型的图片场景池 - 每天随机选一个，让图片多变
GREETING_TYPE_IMAGE_PROMPTS = {
    "早安": [
        # 场景1: 窗边早餐
        "flat vector illustration, cute kawaii style, breakfast table by sunny window, steaming coffee cup and croissant, fresh orange juice in glass, warm golden morning light rays, vase with small yellow flowers, cozy home atmosphere, soft orange and cream colors, no text, no clock, minimalist design, digital art",
        # 场景2: 公园晨跑
        "flat vector illustration, cute kawaii style, morning park scene with jogging path, sunrise sky in pink and orange, trees with morning dew, person stretching on grass, birds chirping on branches, fresh energetic vibe, soft pastel colors, no text, no clock, minimalist design, digital art",
        # 场景3: 猫咪早安
        "flat vector illustration, cute kawaii style, cute cat stretching on bed in morning sunlight, window with sunrise view, coffee mug on nightstand, sleepy yawning face, warm orange glow, adorable cozy feeling, soft peach and white colors, no text, no clock, minimalist design, digital art",
        # 场景4: 花园清晨
        "flat vector illustration, cute kawaii style, small garden with morning dewdrops on flowers, watering can and gardening tools, butterflies flying, sunrise golden light through leaves, peaceful cottage vibe, soft green and yellow colors, no text, no clock, minimalist design, digital art",
        # 场景5: 书桌晨光
        "flat vector illustration, cute kawaii style, study desk with morning light, notebook and pen, cup of tea, small succulent plant, window showing sunrise, ready for productive day, warm yellow and cream colors, no text, no clock, minimalist design, digital art",
    ],
    
    "午饭": [
        # 场景1: 便当盒
        "flat vector illustration, cute kawaii style, colorful bento box with rice balls, cherry tomatoes, cucumber slices, cute panda-shaped rice, chopsticks and napkin, bright midday sunlight, fresh healthy meal, soft orange and green colors, no text, no clock, minimalist design, digital art",
        # 场景2: 面馆
        "flat vector illustration, cute kawaii style, steaming bowl of ramen noodles, chopsticks lifting noodles, egg and green onions on top, cozy Japanese restaurant window seat, warm afternoon light, appetizing food illustration, soft red and yellow colors, no text, no clock, minimalist design, digital art",
        # 场景3: 沙拉轻食
        "flat vector illustration, cute kawaii style, fresh salad bowl with lettuce tomatoes avocado, grilled chicken slices, fork and lemon wedge, bright window view, healthy lunch concept, soft green and pink colors, no text, no clock, minimalist design, digital art",
        # 场景4: 公司茶水间
        "flat vector illustration, cute kawaii style, office pantry scene, microwave and fridge, colleague chatting with lunch box, coffee machine, bright fluorescent lights, friendly workplace vibe, soft blue and orange colors, no text, no clock, minimalist design, digital art",
        # 场景5: 外卖小哥
        "flat vector illustration, cute kawaii style, delivery rider with food box on scooter, city street noon scene, buildings and trees, sunny day delivery, cheerful lunch time, soft yellow and green colors, no text, no clock, minimalist design, digital art",
    ],
    
    "午休": [
        # 场景1: 办公椅小憩
        "flat vector illustration, cute kawaii style, person resting head on desk with folded arms, soft eye mask, peaceful sleeping face, office desk with laptop closed, quiet afternoon calm, soft blue and gray colors, no text, no clock, minimalist design, digital art",
        # 场景2: 楼下公园散步
        "flat vector illustration, cute kawaii style, small city park with benches and trees, person sitting on bench reading book, pigeons walking around, dappled afternoon sunlight through leaves, relaxing outdoor break, soft green and cream colors, no text, no clock, minimalist design, digital art",
        # 场景3: 咖啡厅角落
        "flat vector illustration, cute kawaii style, cozy cafe corner booth, person with headphones listening to music, soft cushion and warm lamp, afternoon coffee break, gentle ambient vibe, soft brown and cream colors, no text, no clock, minimalist design, digital art",
        # 场景4: 拉伸放松
        "flat vector illustration, cute kawaii style, person doing yoga stretch in office corner, yoga mat on floor, relaxed pose, soft afternoon light from window, wellness break concept, soft purple and white colors, no text, no clock, minimalist design, digital art",
        # 场景5: 舞台午睡
        "flat vector illustration, cute kawaii style, cute dog sleeping on sofa with blanket, afternoon sunlight through curtains, peaceful nap time scene, cozy home living room, warm beige and soft blue colors, no text, no clock, minimalist design, digital art",
    ],
    
    "下午茶": [
        # 场景1: 奶茶时光
        "flat vector illustration, cute kawaii style, bubble tea cup with colorful pearls, straw and cute bear lid, sweet afternoon treat, bright office desk, refreshing beverage break, soft pink and cream colors, no text, no clock, minimalist design, digital art",
        # 场景2: 马卡龙拼盘
        "flat vector illustration, cute kawaii style, plate of colorful macarons in pink yellow green purple, coffee cup beside, elegant tea party setting, afternoon indulgence, soft pastel rainbow colors, no text, no clock, minimalist design, digital art",
        # 场景3: 办公零食
        "flat vector illustration, cute kawaii style, desk snack drawer opened, cookies chips chocolate bars and nuts, colleague sharing treats, fun afternoon break moment, soft yellow and brown colors, no text, no clock, minimalist design, digital art",
        # 场景4: 果切盘
        "flat vector illustration, cute kawaii style, fresh fruit platter with watermelon slices, orange segments, grapes and berries, refreshing afternoon energy boost, healthy office snack, soft red and green colors, no text, no clock, minimalist design, digital art",
        # 场景5: 下午茶聊天
        "flat vector illustration, cute kawaii style, two colleagues chatting at office table, tea cups and small cakes, relaxed laughter and bonding, warm afternoon companionship, soft orange and pink colors, no text, no clock, minimalist design, digital art",
    ],
    
    "下班": [
        # 场景1: 日落归途
        "flat vector illustration, cute kawaii style, beautiful sunset sky with orange pink purple gradient, silhouette of person walking home on city street, streetlights starting to glow, warm evening atmosphere, soft warm sunset colors, no text, no clock, minimalist design, digital art",
        # 场景2: 地铁晚高峰
        "flat vector illustration, cute kawaii style, subway train interior with tired but smiling commuters, city lights through window, headphones and phones, journey home after work, soft blue and orange colors, no text, no clock, minimalist design, digital art",
        # 场景3: 打卡下班
        "flat vector illustration, cute kawaii style, office elevator door opening, clock-out moment, colleagues waving goodbye, freedom feeling after long day, relief and joy, soft cream and gold colors, no text, no clock, minimalist design, digital art",
        # 场景4: 街边美食
        "flat vector illustration, cute kawaii style, street food stall at dusk, skewers and snacks cooking, hungry workers lining up, evening city vibe, tempting food smell, soft orange and red colors, no text, no clock, minimalist design, digital art",
        # 场景5: 回家开门
        "flat vector illustration, cute kawaii style, apartment door key in hand, warm home lights inside waiting, cat peeking through door, coming home after work comfort, soft yellow and cream colors, no text, no clock, minimalist design, digital art",
    ],
    
    "晚安": [
        # 场景1: 睡前阅读
        "flat vector illustration, cute kawaii style, person reading book in bed with soft bedside lamp, warm blanket and pillows, peaceful bedtime routine, cozy night atmosphere, soft yellow and deep blue colors, no text, no clock, minimalist design, digital art",
        # 场景2: 星空窗景
        "flat vector illustration, cute kawaii style, bedroom window showing starry night sky, crescent moon and twinkling stars, soft curtains, peaceful night view, dreamy sleep mood, deep blue and silver colors, no text, no clock, minimalist design, digital art",
        # 场景3: 猫咪陪睡
        "flat vector illustration, cute kawaii style, cute cat curled up sleeping on bed pillow, cozy night blanket, person's hand gently petting, warm bedtime companionship, soft cream and blue colors, no text, no clock, minimalist design, digital art",
        # 场景4: 睡前护肤
        "flat vector illustration, cute kawaii style, bathroom vanity with skincare products, gentle night routine, soft mirror light, self-care before sleep, relaxing evening ritual, soft pink and white colors, no text, no clock, minimalist design, digital art",
        # 场景5: 抱枕入睡
        "flat vector illustration, cute kawaii style, person hugging soft pillow with closed eyes, cozy duvet and blanket, peaceful sleeping pose, sweet dreams coming, soft lavender and deep blue colors, no text, no clock, minimalist design, digital art",
    ],
}


def greeting_image_gen_node(
    state: GreetingImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GreetingImageGenOutput:
    """
    title: 问候图片生成
    desc: 根据问候类型生成治愈系配图，每天随机场景不重复，使用AI图片生成服务
    integrations: 图片生成
    """
    ctx = runtime.context
    greeting_type = state.greeting_type
    
    # 获取今天的日期数字（用于随机选择场景）
    today = datetime.datetime.now()
    date_seed = int(today.strftime("%Y%m%d"))  # 20260611 -> 20260611
    
    # 获取对应类型的场景池
    scene_prompts = GREETING_TYPE_IMAGE_PROMPTS.get(greeting_type, GREETING_TYPE_IMAGE_PROMPTS["早安"])
    
    # 使用日期作为随机种子，保证同一天选同一个场景
    random.seed(date_seed)
    scene_index = random.randint(0, len(scene_prompts) - 1)
    image_prompt = scene_prompts[scene_index]
    
    # 获取风格描述（用于日志）
    style_info = GREETING_TYPE_IMAGE_STYLE.get(greeting_type, "治愈系插画")
    logger.info(f"图片风格: {style_info}")
    logger.info(f"今日场景序号: {scene_index + 1}/{len(scene_prompts)}")
    logger.info(f"图片提示词: {image_prompt}")
    
    # 使用图片生成客户端（默认配置）
    try:
        img_client = ImageGenerationClient()
        logger.info(f"图片生成客户端初始化成功")
        logger.info(f"base_url: {img_client.config.base_url}")
        logger.info(f"api_key前10字符: {img_client.config.api_key[:10] if img_client.config.api_key else '无'}...")
    except Exception as init_err:
        logger.error(f"图片生成客户端初始化失败: {init_err}")
        # 初始化失败，直接使用picsum
        image_url = f"https://picsum.photos/seed/{today}/800/600"
        logger.info(f"初始化失败，使用picsum备选: {image_url}")
        return GreetingImageGenOutput(
            greeting_image_url=image_url,
            image_prompt=image_prompt,
            greeting_type=greeting_type
        )
    
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