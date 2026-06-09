#!/bin/bash
# 启动早安问候定时调度器
# 每天早上 9:30 自动运行早安问候工作流

cd /workspace/projects

echo "=========================================="
echo "早安问候定时调度器"
echo "调度时间: 每天 09:30"
echo "=========================================="

# 设置环境变量
export PYTHONPATH=/workspace/projects:/workspace/projects/src

# 启动调度器
python src/scheduler/greeting_scheduler.py