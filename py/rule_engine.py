# coding: utf-8
from collections import namedtuple
import logging
import sys

if sys.version_info[0] == 3:
    from functools import reduce

logging.basicConfig(filename='learning_duration.log', level=logging.INFO)
log = logging.getLogger(__name__)

# Status = namedtuple('Status', 'done, msgs')

# show use `return`, however `return` is the keyword of python
unit = lambda sds: ((True, []), sds)


def bind(m_status, strategy_rule):
    def _(sds):
        (done, msgs), sds = m_status(sds)

        if not done:
            return (done, msgs), sds

        (done_, msgs_), sds_ = strategy_rule(sds)
        return (done and done_, msgs + msgs_), sds_
    return _


def build_schedule_rule(rule):
    """关于单元学习的开始时间/结束时间的约束"""
    begin = rule['value']['begin']
    end = rule['value']['end']
    def _(sds):
        now = sds.get('schedule_rule')
        is_ok = begin <= now and now < end
        if is_ok:
            msg = 'You can done the work now'
        else:
            msg = ('Wait %s second' % (begin - now)) if begin > now else ('You are late: %s second' % (end - now))
        return (is_ok, [msg]), sds
    return _


def build_task_mini_score_pct(rule):
    """关于单元内所有练习模块下的Task的最低正确率的约束"""
    score_pct = rule['value']
    def _(sds):
        grades = sds.get('task_mini_score_pct')
        (max_grade, grade) = reduce(lambda acc, x: (acc[0] + x[0], acc[1] + x[1]), grades, (0, 0))
        current_score_pct = 1 if max_grade == 0 else float(grade)/max_grade
        is_ok = current_score_pct >= score_pct
        msg = 'Task is passed' if is_ok else 'Task is not passed'
        return (is_ok, [msg]), sds
    return _
    

def build_unit_test_mini_score_pct(rule):
    """关于单元测试模块的最低正确率的约束"""
    score_pct = rule['value']
    def _(sds):
        grades = sds.get('unit_test_mini_score_pct')
        (max_grade, grade) = reduce(lambda acc, x: (acc[0] + x[0], acc[1] + x[1]), grades, (0, 0))
        current_score_pct = 1 if max_grade == 0 else float(grade)/max_grade
        is_ok = current_score_pct >= score_pct
        msg = 'UT is passed' if is_ok else 'UT is not passed'
        return (is_ok, [msg]), sds
    return _


def build_learning_duration(rule):
    """关于单元内所有微课+单元测试的学习时长的最低要求"""
    expected_learning_duration = rule['value']
    def _(sds):
        learning_duration = sds.get('learning_duration')
        is_ok = learning_duration >= expected_learning_duration
        msg = '`learning_duration` is passed' if is_ok else '`learning_duration` is not passed'
        return (is_ok, [msg]), sds
    return _

RULE_TYPE_MAP = [
    ("schedule", "schedule_rule", build_schedule_rule),
    ("task", "task_mini_score_pct", build_task_mini_score_pct),
    ("unit_test", "unit_test_mini_score_pct", build_unit_test_mini_score_pct),
    ("learning_duration", "learning_duration", build_learning_duration),
]
RULE_TYPE_ORDER = list(map(lambda x: x[1], RULE_TYPE_MAP))
MAP_FOR_BUILD_RULE = dict(map(lambda x: x[1:], RULE_TYPE_MAP))


def buildEngine(chapter_strategy):
    rs = chapter_strategy['rules']

    # sort the sub-rules before build the RULE
    rs.sort(key=lambda x: RULE_TYPE_ORDER.index(x['type']))

    rules = map(lambda r: MAP_FOR_BUILD_RULE[r['type']](r), rs)
    return reduce(bind, rules, unit)

