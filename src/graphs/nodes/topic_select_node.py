"""
话题选择节点
根据笔记类型和主题方向，智能选择合适的话题
"""

import os
import json
import random
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import TopicSelectInput, TopicSelectOutput


# 预定义话题库（根据年轻打工人群体兴趣设计）
TOPIC_LIBRARY: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "养生打工人": {
        "收藏型": [
            {"topic": "办公室养生小妙招", "desc": "分享办公场景下的养生技巧，如正确坐姿、眼部放松等"},
            {"topic": "打工人的健康早餐清单", "desc": "适合忙碌上班族的营养早餐推荐"},
            {"topic": "缓解颈椎酸痛的5个动作", "desc": "针对久坐人群的颈椎保健指南"},
            {"topic": "上班族必备养生茶配方", "desc": "提神醒脑又养生茶饮合集"},
            {"topic": "午休20分钟养生指南", "desc": "如何在短暂午休中有效恢复精力"},
        ],
        "讨论型": [
            {"topic": "你有什么办公室养生秘籍？", "desc": "邀请用户分享自己的养生小技巧"},
            {"topic": "熬夜加班后如何快速恢复？", "desc": "讨论熬夜后的身体恢复经验"},
            {"topic": "打工人的一天养生时间表", "desc": "征集大家日常养生时间安排"},
            {"topic": "你最想改善的健康问题是什么？", "desc": "了解打工人的健康痛点"},
        ],
    },
    "赚钱爱自己": {
        "收藏型": [
            {"topic": "打工人的理财入门清单", "desc": "适合上班族的投资理财基础知识"},
            {"topic": "副业赚钱的10个思路", "desc": "适合下班后尝试的副业方向"},
            {"topic": "省钱但不降质的消费技巧", "desc": "如何在保证生活质量的前提下节省开支"},
            {"topic": "职场升薪的实用建议", "desc": "如何在工作中提升薪资待遇"},
            {"topic": "打工人必备的省钱APP合集", "desc": "实用省钱工具推荐"},
        ],
        "讨论型": [
            {"topic": "你的第一笔工资是怎么花的？", "desc": "分享第一次拿到工资的经历和感受"},
            {"topic": "打工人如何平衡花钱与攒钱？", "desc": "讨论消费与储蓄的平衡之道"},
            {"topic": "你有什么省钱小妙招？", "desc": "征集日常省钱技巧"},
            {"topic": "副业真的值得做吗？", "desc": "讨论副业的利弊和选择"},
        ],
    },
    "职场成长": {
        "收藏型": [
            {"topic": "职场新人必备技能清单", "desc": "刚入职需要掌握的核心技能"},
            {"topic": "高效沟通的5个技巧", "desc": "提升职场沟通效率的方法"},
            {"topic": "打工人必备的办公软件技巧", "desc": "提升工作效率的工具使用指南"},
            {"topic": "如何写出高质量的工作邮件", "desc": "职场邮件写作规范和技巧"},
            {"topic": "会议记录的高效模板", "desc": "标准化会议记录格式"},
        ],
        "讨论型": [
            {"topic": "你遇到过哪些职场难题？", "desc": "征集职场困境和解决经验"},
            {"topic": "职场新人最容易踩的坑", "desc": "讨论新人常见的错误和教训"},
            {"topic": "如何与不同性格的同事相处？", "desc": "讨论职场人际关系处理"},
            {"topic": "你觉得工作中最重要的能力是什么？", "desc": "讨论核心职场能力"},
        ],
    },
    "生活小技巧": {
        "收藏型": [
            {"topic": "打工人的独居生活指南", "desc": "单身上班族的日常生活技巧"},
            {"topic": "租房必看的避坑清单", "desc": "租房注意事项和经验总结"},
            {"topic": "通勤路上的时间利用技巧", "desc": "如何在通勤时间提升自我"},
            {"topic": "打工人的周末充电计划", "desc": "周末休息和学习的安排"},
            {"topic": "上班族的时间管理法则", "desc": "高效利用时间的实用方法"},
        ],
        "讨论型": [
            {"topic": "你的一天是如何安排的？", "desc": "征集打工人的日程安排"},
            {"topic": "租房vs买房你怎么选？", "desc": "讨论住房选择的考量因素"},
            {"topic": "通勤太累怎么办？", "desc": "讨论通勤疲劳的缓解方法"},
            {"topic": "下班后你最想做的是什么？", "desc": "了解打工人的下班生活偏好"},
        ],
    },
}


def topic_select_node(
    state: TopicSelectInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> TopicSelectOutput:
    """
    title: 话题选择
    desc: 根据笔记类型和主题方向，从话题库中智能选择合适的话题
    integrations: 无外部集成
    """
    note_type = state.note_type
    theme_direction = state.theme_direction
    
    # 从话题库中选择
    if theme_direction in TOPIC_LIBRARY:
        topics_by_type = TOPIC_LIBRARY.get(theme_direction, {})
        topic_list = topics_by_type.get(note_type, [])
        
        if topic_list:
            # 随机选择一个话题
            selected = random.choice(topic_list)
            selected_topic = selected.get("topic", "")
            topic_description = selected.get("desc", "")
            
            return TopicSelectOutput(
                selected_topic=selected_topic,
                topic_description=topic_description
            )
    
    # 如果没有匹配的话题，使用默认话题
    default_topic = "打工人日常分享"
    default_desc = "分享打工人的日常生活和心得体会"
    
    return TopicSelectOutput(
        selected_topic=default_topic,
        topic_description=default_desc
    )