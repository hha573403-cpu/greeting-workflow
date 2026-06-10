"""
笔记内容推送节点
将生成的笔记内容推送到企业微信
"""

import json
import requests
import logging
import os
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import NotePushInput, NotePushOutput

logger = logging.getLogger(__name__)


def note_push_node(
    state: NotePushInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> NotePushOutput:
    """
    title: 笔记内容推送
    desc: 将生成的小红书笔记内容推送到企业微信群，包含标题、正文、标签和配图
    integrations: 企业微信机器人
    """
    
    ctx = runtime.context
    logger.info(f"笔记标题: {state.title}")
    logger.info(f"标签: {','.join(state.tags)}")
    logger.info(f"配图URL: {state.image_url}")
    
    # 获取企业微信 Webhook Key
    webhook_key = os.getenv("WECHAT_WEBHOOK_KEY", "")
    if not webhook_key:
        logger.error("❌ 企业微信 Webhook Key 未配置")
        return NotePushOutput(
            push_status="失败",
            push_message="企业微信 Webhook Key 未配置"
        )
    
    webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    
    # 构建推送内容 - 卡片消息格式
    title = state.title
    content = state.content
    tags_str = " ".join([f"#{tag}" for tag in state.tags])
    image_url = state.image_url
    
    # 构建完整内容
    full_content = f"{content}\n\n{tags_str}"
    
    # 发送卡片消息
    card_data: Dict[str, Any] = {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "text_notice",
            "source": {
                "title": "小红书笔记生成",
                "desc": f"类型: {state.note_type}",
                "icon_url": "https://img.icons8.com/color/96/notepad.png"
            },
            "main_title": {
                "title": title,
                "desc": full_content[:500] if len(full_content) > 500 else full_content
            },
            "sub_title_text": f"主题: {state.theme_direction}",
            "card_action": {
                "type": 1,
                "url": image_url,
                "appid": ""
            }
        }
    }
    
    try:
        # 发送卡片消息
        resp = requests.post(webhook_url, json=card_data, timeout=10)
        resp_data = resp.json()
        
        if resp_data.get("errcode", 0) != 0:
            logger.error(f"企业微信卡片推送失败: {resp_data}")
            # 尝试发送文本消息作为备选
            text_data: Dict[str, Any] = {
                "msgtype": "text",
                "text": {
                    "content": f"【小红书笔记生成】\n\n标题: {title}\n\n内容: {content}\n\n标签: {tags_str}\n\n配图: {image_url}"
                }
            }
            resp2 = requests.post(webhook_url, json=text_data, timeout=10)
            if resp2.json().get("errcode", 0) == 0:
                logger.info("✅ 已通过文本消息推送")
                return NotePushOutput(
                    push_status="成功",
                    push_message="笔记内容已通过文本消息推送"
                )
            else:
                return NotePushOutput(
                    push_status="失败",
                    push_message=f"推送失败: {resp2.json()}"
                )
        
        logger.info("✅ 笔记内容卡片推送成功")
        
        # 发送配图消息
        if image_url and image_url.startswith("http"):
            image_data: Dict[str, Any] = {
                "msgtype": "image",
                "image": {
                    "url": image_url
                }
            }
            resp3 = requests.post(webhook_url, json=image_data, timeout=10)
            if resp3.json().get("errcode", 0) == 0:
                logger.info("✅ 配图推送成功")
        
        return NotePushOutput(
            push_status="成功",
            push_message="笔记内容和配图已成功推送"
        )
        
    except Exception as e:
        logger.error(f"❌ 推送失败: {e}")
        return NotePushOutput(
            push_status="失败",
            push_message=f"推送异常: {str(e)}"
        )