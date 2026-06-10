#!/usr/bin/env python3
"""
小红书笔记生成工作流调度器
支持两种模式：
1. 问候推送模式：早安/午饭/午休/下午茶/下班/晚安，全天候陪伴打工人
2. 笔记内容模式：生成小红书笔记内容（收藏型或讨论型）
"""
import os
import sys
import json
import logging
import datetime
import argparse
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))

# 设置日志（使用项目目录下的logs）
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(PROJECT_PATH, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, 'scheduler.log')),
    ]
)
logger = logging.getLogger(__name__)

# 导入工作流
from graphs.graph import main_graph


def run_greeting_push(greeting_type: str):
    """执行问候推送
    
    Args:
        greeting_type: 问候类型，早安/午饭/午休/下午茶/下班/晚安
    """
    logger.info("=" * 60)
    logger.info(f"开始执行{greeting_type}推送...")
    
    today = datetime.datetime.now()
    logger.info(f"今天是 {today.strftime('%Y年%m月%d日 %A')}")
    
    try:
        logger.info(f">>> 正在生成{greeting_type}内容...")
        
        result = main_graph.invoke({
            "content_type": "问候推送",
            "greeting_type": greeting_type
        })
        
        greeting_content = result.get("greeting_content", "")
        greeting_image_url = result.get("greeting_image_url", "")
        push_status = result.get("push_status", "未知")
        
        logger.info(f"{greeting_type}内容已生成")
        logger.info(f"推送状态: {push_status}")
        
        if push_status == "成功":
            logger.info(f"✅ {greeting_type}推送成功！已推送到企业微信")
        else:
            logger.warning(f"⚠️ 推送状态: {push_status}")
        
        logger.info("=" * 60)
        logger.info(f"{greeting_type}推送工作流执行完成!")
        
        # 输出结果JSON
        output = {
            "content_type": "问候推送",
            "greeting_type": greeting_type,
            "greeting_content": greeting_content,
            "greeting_image_url": greeting_image_url,
            "push_status": push_status
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}


def run_note_gen(note_type: str, theme_direction: str):
    """执行笔记内容生成
    
    Args:
        note_type: 笔记类型，"收藏型" 或 "讨论型"
        theme_direction: 主题方向，如 "养生打工人"、"赚钱爱自己"等
    """
    logger.info("=" * 60)
    logger.info("开始执行笔记内容生成...")
    logger.info(f"笔记类型: {note_type}")
    logger.info(f"主题方向: {theme_direction}")
    
    try:
        logger.info(">>> 正在选择话题并生成内容...")
        
        result = main_graph.invoke({
            "content_type": "笔记内容",
            "note_type": note_type,
            "theme_direction": theme_direction
        })
        
        title = result.get("title", "")
        content = result.get("content", "")
        tags = result.get("tags", [])
        image_url = result.get("image_url", "")
        
        logger.info(f"笔记标题: {title}")
        logger.info(f"标签: {', '.join(tags)}")
        logger.info(f"配图URL: {image_url}")
        
        logger.info("=" * 60)
        logger.info("笔记内容生成完成!")
        
        # 输出结果JSON
        output = {
            "content_type": "笔记内容",
            "note_type": note_type,
            "theme_direction": theme_direction,
            "title": title,
            "content": content,
            "tags": tags,
            "image_url": image_url
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}


def main():
    """主入口，支持命令行参数"""
    parser = argparse.ArgumentParser(description="小红书笔记生成工作流")
    parser.add_argument(
        "--mode", 
        choices=["greeting", "note"],
        default="greeting",
        help="运行模式: greeting(问候推送) 或 note(笔记内容)"
    )
    parser.add_argument(
        "--greeting-type",
        choices=["早安", "午饭", "午休", "下午茶", "下班", "晚安"],
        default="早安",
        help="问候类型（仅greeting模式有效）"
    )
    parser.add_argument(
        "--note-type",
        choices=["收藏型", "讨论型"],
        default="收藏型",
        help="笔记类型（仅note模式有效）"
    )
    parser.add_argument(
        "--theme",
        default="养生打工人",
        help="主题方向（仅note模式有效），如: 养生打工人、赚钱爱自己、职场成长"
    )
    
    args = parser.parse_args()
    
    if args.mode == "greeting":
        logger.info(f"触发 {args.greeting_type} 推送")
        run_greeting_push(args.greeting_type)
    else:
        logger.info("手动触发 - 执行笔记内容生成")
        run_note_gen(args.note_type, args.theme)


if __name__ == "__main__":
    main()