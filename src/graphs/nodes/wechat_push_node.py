"""
微信推送节点
将问候内容推送到企业微信群
支持：早安/午饭/午休/下午茶/下班/晚安 六种类型
"""

import os
import json
import re
import requests
import base64
import hashlib
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import WechatPushInput, WechatPushOutput


# 各类型的标题和图标
GREETING_TYPE_TITLE = {
    "早安": "☀️ 早安，打工人！",
    "午饭": "🍜 该吃饭啦！",
    "午休": "💤 午休时间~",
    "下午茶": "☕ 下午茶时刻",
    "下班": "🎉 下班啦！辛苦一天！",
    "晚安": "🌙 晚安，好梦~"
}


def get_webhook_key() -> str:
    """获取企业微信机器人webhook_key
    优先从环境变量读取，其次从集成配置读取
    """
    # 优先从环境变量读取（用于GitHub Actions等外部环境）
    env_key = os.getenv("WECHAT_WEBHOOK_KEY", "")
    if env_key:
        return env_key
    
    # 其次从集成配置读取（用于本地开发环境）
    try:
        from coze_workload_identity import Client
        client = Client()
        wechat_bot_credential = client.get_integration_credential("integration-wechat-bot")
        data = json.loads(wechat_bot_credential)
        
        # 支持 webhook_url 或 webhook_key 两种字段名
        webhook_value = data.get("webhook_key") or data.get("webhook_url") or ""
        
        # 如果是完整URL，提取key参数
        if "https" in webhook_value:
            match = re.search(r"key=([a-zA-Z0-9-]+)", webhook_value)
            if match:
                return match.group(1)
        
        return webhook_value
    except Exception:
        return ""


def wechat_push_node(
    state: WechatPushInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> WechatPushOutput:
    """
    title: 微信推送
    desc: 将问候文案和配图推送到企业微信群，支持早安/午饭/午休/下午茶/下班/晚安
    integrations: 企业微信机器人
    """
    
    # 获取webhook_key
    try:
        webhook_key = get_webhook_key()
        if not webhook_key:
            return WechatPushOutput(
                push_status="失败",
                push_message="未配置企业微信机器人webhook_key"
            )
    except Exception as e:
        return WechatPushOutput(
            push_status="失败",
            push_message=f"获取webhook_key失败: {str(e)}"
        )
    
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    headers = {"Content-Type": "application/json"}
    
    # 获取推送内容
    greeting_type = state.greeting_type
    greeting_content = state.greeting_content
    greeting_image_url = state.greeting_image_url
    
    # 获取对应类型的标题
    type_title = GREETING_TYPE_TITLE.get(greeting_type, "🔔 温馨提醒")
    
    push_result: Dict[str, Any] = {}
    
    try:
        # 1. 先发送图片
        if greeting_image_url:
            # 下载图片并转为base64
            img_response = requests.get(greeting_image_url, timeout=30)
            img_response.raise_for_status()
            img_data = img_response.content
            img_b64 = base64.b64encode(img_data).decode("utf-8")
            img_md5 = hashlib.md5(img_data).hexdigest()
            
            image_payload = {
                "msgtype": "image",
                "image": {
                    "base64": img_b64,
                    "md5": img_md5
                }
            }
            
            img_send_response = requests.post(send_url, json=image_payload, headers=headers, timeout=15)
            img_send_response.raise_for_status()
        
        # 2. 发送文案
        markdown_content = f"""
## {type_title}

{greeting_content if greeting_content else '内容已生成，请查看详细内容'}

---
> 📌 **提示**: 内容已生成，可复制发布到小红书
"""
        
        text_payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown_content
            }
        }
        
        text_response = requests.post(send_url, json=text_payload, headers=headers, timeout=15)
        text_response.raise_for_status()
        text_result = text_response.json()
        
        if text_result.get("errcode", 0) == 0:
            push_result = {
                "status": "成功",
                "message": f"{greeting_type}推送成功"
            }
        else:
            push_result = {
                "status": "失败",
                "message": text_result.get("errmsg", "推送失败")
            }
    
    except Exception as e:
        push_result = {
            "status": "失败",
            "message": f"推送异常: {str(e)}"
        }
    
    return WechatPushOutput(
        push_status=push_result.get("status", "失败"),
        push_message=push_result.get("message", "")
    )