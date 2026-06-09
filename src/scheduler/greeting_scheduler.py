"""
定时调度器 - 每天自动运行早安问候+每日待办工作流
每天早上 9:30 自动触发并推送到企业微信
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

# 设置日志 - 使用项目目录下的logs文件夹
LOG_DIR = os.path.join(PROJECT_PATH, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'scheduler.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入工作流和推送功能
from graphs.graph import main_graph
from graphs.nodes.greeting_gen_node import greeting_gen_node
from graphs.nodes.greeting_image_gen_node import greeting_image_gen_node
from graphs.nodes.daily_todo_node import daily_todo_node
from graphs.nodes.wechat_push_node import wechat_push_node


def run_daily_push():
    """执行每日推送：每日待办 + 早安问候"""
    logger.info("=" * 60)
    logger.info("开始执行每日推送工作流...")
    
    today = datetime.datetime.now()
    logger.info(f"今天是 {today.strftime('%Y年%m月%d日 %A')}")
    
    try:
        # 1. 生成每日待办内容
        logger.info(">>> 正在生成每日待办内容...")
        todo_result = daily_todo_node(
            {"date_info": {}},
            {"metadata": {"llm_cfg": "config/daily_todo_cfg.json"}},
            {"context": None}
        )
        todo_content = todo_result.daily_todo_content
        logger.info(f"每日待办已生成，长度: {len(todo_content)}字")
        
        # 2. 生成早安问候内容
        logger.info(">>> 正在生成早安问候内容...")
        greeting_result = greeting_gen_node(
            {"greeting_style": "温馨治愈"},
            {"metadata": {"llm_cfg": "config/greeting_gen_cfg.json"}},
            {"context": None}
        )
        greeting_content = greeting_result.greeting_content
        logger.info(f"早安问候已生成，长度: {len(greeting_content)}字")
        
        # 3. 生成早安问候配图
        logger.info(">>> 正在生成早安问候配图...")
        greeting_img_result = greeting_image_gen_node(
            {"greeting_content": greeting_content, "greeting_style": "温馨治愈"},
            {},
            {"context": None}
        )
        greeting_image_url = greeting_img_result.greeting_image_url
        logger.info(f"早安问候配图已生成")
        
        # 4. 推送到企业微信（整合两条内容）
        logger.info(">>> 正在推送到企业微信...")
        push_result = wechat_push_node(
            {
                "greeting_content": greeting_content,
                "greeting_image_url": greeting_image_url,
                "daily_todo_content": todo_content,
                "todo_image_url": ""  # 待办不单独生成图片，用早安图片
            },
            {},
            {"context": None}
        )
        push_status = push_result.push_status
        
        logger.info(f"推送状态: {push_status}")
        
        if push_status == "成功":
            logger.info("✅ 每日推送成功！早安问候+每日待办已推送到企业微信")
        else:
            logger.warning(f"⚠️ 推送状态: {push_status}")
        
        logger.info("=" * 60)
        logger.info("每日推送工作流执行完成!")
        
        return {
            "todo_content": todo_content,
            "greeting_content": greeting_content,
            "greeting_image_url": greeting_image_url,
            "push_status": push_status
        }
        
    except Exception as e:
        logger.error(f"❌ 每日推送执行失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"push_status": "失败", "error": str(e)}


def start_scheduler():
    """启动定时调度器"""
    logger.info("=" * 60)
    logger.info("🚀 启动每日推送定时调度器")
    logger.info("⏰ 推送时间: 每天 09:30")
    logger.info("📱 推送内容: 每日待办 + 早安问候文案+配图")
    logger.info("📍 推送渠道: 企业微信群机器人")
    logger.info("=" * 60)
    
    # 设置定时任务
    schedule.every().day.at("09:30").do(run_daily_push)
    
    logger.info("调度器已启动，等待下次触发时间...")
    
    # 显示下次触发时间
    next_run = schedule.next_run()
    logger.info(f"下次触发时间: {next_run}")
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    start_scheduler()