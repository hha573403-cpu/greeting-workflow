#!/usr/bin/env python3
"""
每日问候定时调度器
每天早上9:30自动生成并推送早安问候+每日待办到企业微信
"""
import os
import sys
import json
import logging
import datetime
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
    """执行每日推送：每日待办 + 早安问候"""
    logger.info("=" * 60)
    logger.info("开始执行每日推送工作流...")
    
    today = datetime.datetime.now()
    logger.info(f"今天是 {today.strftime('%Y年%m月%d日 %A')}")
    
    try:
        # 使用工作流的invoke方法运行（正确的调用方式）
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


if __name__ == "__main__":
    # 直接执行一次推送（用于GitHub Actions调用）
    logger.info("GitHub Actions触发 - 执行每日推送")
    result = run_daily_push()
    print(json.dumps(result, ensure_ascii=False, indent=2))