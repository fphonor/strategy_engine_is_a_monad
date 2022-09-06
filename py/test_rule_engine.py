# coding: utf-8
import unittest
import copy
import logging
from strategy_engine import buildEngine

logging.basicConfig(filename='learning_duration.log', level=logging.INFO)
log = logging.getLogger(__name__)

CHAPTER_STRATEGY = {
    "block_id": "0afsd0afsd0afsd0afsdffff0afsdf",    # chapter_block_id
    "rules": [
        {
            "type": "schedule_rule",                 # 关于单元学习的开始时间/结束时间的约束
            "value": {
                "begin": 1469584482,                 # 开始时间
                "end": 1470584482                    # 结束时间
            }
        }, {
            "type": "task_mini_score_pct",           # 关于单元内所有练习模块下的Task的最低正确率的约束
            "value": 0.6                             # 0.6的意思是最低答题正确率为 60%
        }, {
            "type": "unit_test_mini_score_pct",      # 关于单元测试模块的最低正确率的约束
            "value": 0.8                             # 0.8的意思是单元测试最低答题正确率为 80%
        }, {
            "type": "learning_duration",             # 关于单元内所有微课+单元测试的学习时长的最低要求
            "value": 3600                            # 3600的意思是3600秒,也就是该单元的最低学习时长的1小时
        }
    ]
}

DATA = {
    "schedule_rule": 503 + 1469583982,
    "task_mini_score_pct": [[1, 1], [1, 0], [1, 0], [1, 1], [1, 1]],
    "unit_test_mini_score_pct": [[1, 1], [1, 0], [1, 1], [1, 1], [1, 1]],
    "learning_duration": 5000
}

def main(DATA):
    import time

    import sys
    if sys.version_info[0] == 3:
        xrange = range

    engine = buildEngine(CHAPTER_STRATEGY)
    n = 1000000
    begin = time.time()

    for i in xrange(n):
        # for _ in xrange(8):
        #     # log.info("abc: %s - %d", "brian", 9)
        #     log.info("abc: brian - 9")
        # log.info("abc: %s - %d", "brian", 9)
        result = engine(DATA)
        # buildEngine(CHAPTER_STRATEGY)(LEARNING_DURATION_DATA)
    print((time.time() - begin)/n)
    # print(engine(DATA))

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = buildEngine(CHAPTER_STRATEGY)

    def test_done(self):
        (result, sds) = self.engine(DATA)
        self.assertTrue(result.done, "it must be done")
        main(DATA)

    def test_not_done_learning_duration(self):
        LEARNING_DURATION_DATA = copy.deepcopy(DATA)
        LEARNING_DURATION_DATA['learning_duration'] = 3000
        (result, sds) = self.engine(LEARNING_DURATION_DATA)
        self.assertTrue(result.done is False, "it must not be done")
        main(LEARNING_DURATION_DATA)

    def test_not_done_schedule_rule(self):
        SCHEDULE_RULE_DATA = copy.deepcopy(DATA)
        SCHEDULE_RULE_DATA['schedule_rule'] = 1469583982
        (result, sds) = self.engine(SCHEDULE_RULE_DATA)
        self.assertTrue(result.done is False, "it must not be done")
        main(SCHEDULE_RULE_DATA)

    def test_not_done_task_mini(self):
        TASK_DATA = copy.deepcopy(DATA)
        TASK_DATA['task_mini_score_pct'] = [[1, 0], [1, 0], [1, 0], [1, 1], [1, 1]]
        (result, sds) = self.engine(TASK_DATA)
        self.assertTrue(result.done is False, "it must not be done")
        main(TASK_DATA)

    def test_not_done_unit_test(self):
        UNIT_TEST_DATA = copy.deepcopy(DATA)
        UNIT_TEST_DATA['unit_test_mini_score_pct'] = [[1, 0], [1, 0], [1, 1], [1, 1], [1, 1]]
        (result, sds) = self.engine(UNIT_TEST_DATA)
        self.assertTrue(result.done is False, "it must not be done")
        main(UNIT_TEST_DATA)

if __name__ == '__main__':
    LEARNING_DURATION_DATA = copy.deepcopy(DATA)
    # LEARNING_DURATION_DATA['learning_duration'] = 3000
    main(LEARNING_DURATION_DATA)
