"""
定时调度器 - 每天自动运行早安问候工作流
每天早上 9:30 自动触发早安问候生成并推送到企业微信
"""
import os
import sys
import json
import time
import schedule
import logging
import datetime

# 设置项目路径
PROJECT_PATH = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, os.path.join(PROJECT_PATH, "src"))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/work/logs/bypass/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入工作流
from graphs.graph import main_graph


def run_greeting_workflow():
    """执行早安问候工作流"""
    logger.info("=" * 50)
    logger.info("开始执行早安问候工作流...")
    
    try:
        # 构造输入参数
        input_data = {
            "content_type": "早安问候",
            "greeting_style": "温馨治愈"
        }
        
        # 获取当前日期，确保每天内容不重复
        today = datetime.datetime.now()
        logger.info(f"今天是 {today.strftime('%Y年%m月%d日 %A')}")
        
        # 执行工作流
        result = main_graph.invoke(input_data)
        
        # 记录结果
        logger.info(f"工作流执行完成!")
        logger.info(f"推送状态: {result.get('push_status', '未知')}")
        
        if result.get('push_status') == '成功':
            logger.info("✅ 早安问候已成功推送到企业微信!")
        else:
            logger.warning(f"⚠️ 推送状态: {result.get('push_status')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {str(e)}")
        raise


def main():
    """主函数 - 启动定时调度"""
    logger.info("=" * 50)
    logger.info("定时调度器启动")
    logger.info("调度时间: 每天 09:30")
    logger.info("任务: 早安问候生成 + 企业微信推送")
    logger.info("=" * 50)
    
    # 设置每天9:30执行
    schedule.every().day.at("09:30").do(run_greeting_workflow)
    
    logger.info("调度器已启动，等待执行...")
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    main()