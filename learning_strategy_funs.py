# coding: utf-8
from collections import namedtuple
import unittest

Status = namedtuple('Status', 'done, time_status, msgs')

unit = lambda sds: (Status(True, True, []), sds)

def bind(m_status, strategy_rule):
    def _(sds):
        (status, sds1) = m_status(sds)
        if not status.done:
            return (status, sds1)
        else:
            return strategy_rule(status, sds1)
    return _

def build_schedule_rule(rule):
    """关于单元学习的开始时间/结束时间的约束"""
    begin = rule['value']['begin']
    end = rule['value']['end']
    def _(status, sds):
        now = sds.get('schedule_rule')
        is_ok = begin <= now and now < end
        if is_ok:
            msg = 'You can done the work now'
        else:
            msg = ('Wait %s second' % (begin - now)) if begin > now else ('You are late: %s second' % (end - now))
        return (Status(is_ok and status.done, is_ok, status.msgs + [msg]), sds)
    return _

def build_task_mini_score_pct(rule):
    """关于单元内所有练习模块下的Task的最低正确率的约束"""
    score_pct = rule['value']
    def _(status, sds):
        grades = sds.get('task_mini_score_pct')
        max_grade, grade = reduce(lambda acc, x: (acc[0] + x[0], acc[1] + x[1]), grades, (0, 0))
        current_score_pct = 1 if max_grade == 0 else float(grade)/max_grade
        is_ok = current_score_pct >= score_pct
        msg = 'Task is passed' if is_ok else 'Task is not passed'
        return (Status(is_ok and status.done, status.time_status, status.msgs + [msg]), sds)
    return _
    
def build_unit_test_mini_score_pct(rule):
    """关于单元测试模块的最低正确率的约束"""
    score_pct = rule['value']
    def _(status, sds):
        grades = sds.get('unit_test_mini_score_pct')
        max_grade, grade = reduce(lambda acc, x: (acc[0] + x[0], acc[1] + x[1]), grades, (0, 0))
        current_score_pct = 1 if max_grade == 0 else float(grade)/max_grade
        is_ok = current_score_pct >= score_pct
        msg = 'UT is passed' if is_ok else 'UT is not passed'
        return (Status(is_ok and status.done, status.time_status, status.msgs + [msg]), sds)
    return _

def build_learning_duration(rule):
    """关于单元内所有微课+单元测试的学习时长的最低要求"""
    expected_learning_duration = rule['value']
    def _(status, sds):
        learning_duration = sds.get('learning_duration')
        is_ok = learning_duration >= expected_learning_duration
        msg = '`learning_duration` is passed' if is_ok else '`learning_duration` is not passed'
        return (Status(is_ok and status.done, status.time_status, status.msgs + [msg]), sds)
    return _

RULE_TYPE_MAP = [
    ("schedule", "schedule_rule", build_schedule_rule),
    ("task", "task_mini_score_pct", build_task_mini_score_pct),
    ("unit_test", "unit_test_mini_score_pct", build_unit_test_mini_score_pct),
    ("learning_duration", "learning_duration", build_learning_duration),
]
RULE_TYPE_ORDER = map(lambda x: x[1], RULE_TYPE_MAP)
MAP_FOR_BUILD_RULE = dict(map(lambda x: x[1:], RULE_TYPE_MAP))


def buildEngine(chapter_strategy):
    rs = chapter_strategy['rules']
    rs.sort(key=lambda x: RULE_TYPE_ORDER.index(x['type']))
    rules = map(lambda r: MAP_FOR_BUILD_RULE[r['type']](r), rs)
    return reduce(bind, rules, unit)


chapter_strategy= {
    "block_id": "0afsd0afsd0afsd0afsdffff0afsdf", # chapter_block_id
    "rules": [
        {
            "type": "schedule_rule",          # 关于单元学习的开始时间/结束时间的约束
            "value": {
                "begin": 1469584482,     # 开始时间
                "end": 1470584482        # 结束时间
            }
        }, {
            "type": "task_mini_score_pct", # 关于单元内所有练习模块下的Task的最低正确率的约束
            "value": 0.6                 # 0.6的意思是最低答题正确率为 60%
        }, {
            "type": "unit_test_mini_score_pct",         # 关于单元测试模块的最低正确率的约束
            "value": 0.8                 # 0.8的意思是单元测试最低答题正确率为 80%
        }, {
            "type": "learning_duration", # 关于单元内所有微课+单元测试的学习时长的最低要求
            "value": 3600                # 3600的意思是3600秒,也就是该单元的最低学习时长的1小时
        }
    ]
}


class TestEngine(unittest.TestCase):
    def test_engine_done(self):
        engine = buildEngine(chapter_strategy)
        result, sds = engine({
            "schedule_rule": 503 + 1469583982,
            "task_mini_score_pct": [[1, 0], [1, 1], [1, 0], [1, 1], [1, 1]],
            "unit_test_mini_score_pct": [[1, 0], [1, 1], [1, 1], [1, 1], [1, 1]],
            "learning_duration": 8000
        })
        self.assertTrue(result.done, "it must be done")

    def test_engine_not_done(self):
        engine = buildEngine(chapter_strategy)
        result, sds = engine({
            "schedule_rule": 503 + 1469583982,
            "task_mini_score_pct": [[1, 0], [1, 1], [1, 0], [1, 1], [1, 1]],
            "unit_test_mini_score_pct": [[1, 0], [1, 1], [1, 1], [1, 1], [1, 1]],
            "learning_duration": 3000,
        })
        self.assertTrue(result.done == False, "it must not be done")
        engine = buildEngine(chapter_strategy)
        result, sds = engine({
            "schedule_rule": 503 + 1469583982,
            "task_mini_score_pct": [[1, 0], [1, 0], [1, 0], [1, 1], [1, 1]],
            "unit_test_mini_score_pct": [[1, 0], [1, 1], [1, 1], [1, 1], [1, 1]],
            "learning_duration": 3000,
        })
        self.assertTrue(result.done == False, "it must not be done")

        result, sds = engine({
            "schedule_rule": 503 + 1460583982,
            "task_mini_score_pct": [[1, 0], [1, 0], [1, 0], [1, 1], [1, 1]],
            "unit_test_mini_score_pct": [[1, 0], [1, 1], [1, 1], [1, 1], [1, 1]],
            "learning_duration": 3000,
        })
        self.assertTrue(result.done == False, "it must not be done")


if __name__ == '__main__':
    import time
    data = {
        "schedule_rule": 503 + 1469583982,
        "task_mini_score_pct": [[1, 0], [1, 1], [1, 0], [1, 1], [1, 1]],
        "unit_test_mini_score_pct": [[1, 0], [1, 1], [1, 1], [1, 1], [1, 1]],
        "learning_duration": 3000,
    }
    import logging
    logging.basicConfig(filename='learning_duration.log', level=logging.INFO)
    log = logging.getLogger(__name__)
    engine = buildEngine(chapter_strategy)
    begin = time.time()
    for i in xrange(1000000):
        # for _ in xrange(8):
        #     log.debug(data)
        result = engine(data)
    print(time.time() - begin)
    #unittest.main()
