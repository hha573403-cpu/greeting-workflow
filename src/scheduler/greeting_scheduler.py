#!/usr/bin/env python3
"""
小红书笔记生成工作流调度器
支持两种模式：
1. 早安问候模式：每天早上9:30自动生成并推送早安问候到企业微信
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


def run_daily_push():
    """执行每日推送：早安问候"""
    logger.info("=" * 60)
    logger.info("开始执行每日推送工作流...")
    
    today = datetime.datetime.now()
    logger.info(f"今天是 {today.strftime('%Y年%m月%d日 %A')}")
    
    try:
        logger.info(">>> 正在生成早安问候内容...")
        
        result = main_graph.invoke({
            "content_type": "早安问候",
            "greeting_style": "温馨治愈"
        })
        
        greeting_content = result.get("greeting_content", "")
        greeting_image_url = result.get("greeting_image_url", "")
        push_status = result.get("push_status", "未知")
        
        logger.info(f"早安问候已生成")
        logger.info(f"推送状态: {push_status}")
        
        if push_status == "成功":
            logger.info("✅ 每日推送成功！早安问候已推送到企业微信")
        else:
            logger.warning(f"⚠️ 推送状态: {push_status}")
        
        logger.info("=" * 60)
        logger.info("每日推送工作流执行完成!")
        
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
        help="运行模式: greeting(早安问候) 或 note(笔记内容)"
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
        # GitHub Actions 默认调用早安问候
        logger.info("GitHub Actions触发 - 执行每日推送")
        run_daily_push()
    else:
        # 笔记内容生成
        logger.info("手动触发 - 执行笔记内容生成")
        run_note_gen(args.note_type, args.theme)


if __name__ == "__main__":
    main()
    result = run_daily_push()
    print(json.dumps(result, ensure_ascii=False, indent=2))