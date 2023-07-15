import os
import logging

from datetime import datetime

class AvgTimeCalc():
    auto_avg_time = 4
    kand_avg_time = 4
    kand_time_diffs = [4, 4, 4, 4, 4, 4, 4, 4]
    auto_time_diffs = [4, 4, 4, 4, 4, 4, 4, 4]
    kand_td_index = 0
    auto_td_index = 0
    executors = {}
    
    ratio = (0, 0)

    @classmethod
    def remove_executor(cls, executor):
        executors: list = cls.executors.get(executor.exec_type)
        executors.remove(executor)

    @classmethod
    def add_executor(cls, executor):
        executors: list = cls.executors.get(executor.exec_type)
        if executors is None:
            cls.executors[executor.exec_type] = []
            executors = cls.executors[executor.exec_type]
        executors.append(executor)

    @classmethod
    def update_ratio(cls):
        cls.ratio = tuple(map(int, os.getenv('GENERAL_PREMIUM_RATIO').split()))
        logging.warning(f'Updating ratio {cls.ratio[0]}/{cls.ratio[1]}')
    
    @classmethod
    def calc_auto_time_diff(cls, coro):
        async def wrapped(*args, **kwargs):
            time_start = datetime.now()
            await coro(*args, **kwargs)
            time_finish = datetime.now()
            time_diff = time_finish - time_start
            cls.add_auto_time_diff(time_diff.total_seconds())
        return wrapped
    
    @classmethod
    def calc_kand_time_diff(cls, coro):
        async def wrapped(*args, **kwargs):
            time_start = datetime.now()
            await coro(*args, **kwargs)
            time_finish = datetime.now()
            time_diff = time_finish - time_start
            cls.add_kand_time_diff(time_diff.total_seconds())
        return wrapped

    @classmethod
    def add_auto_time_diff(cls, td):
        cls.auto_td_index = (cls.auto_td_index + 1) % len(cls.auto_time_diffs)
        cls.auto_time_diffs[cls.auto_td_index] = td
        cls.auto_avg_time = sum(cls.auto_time_diffs) / len(cls.auto_time_diffs)

    @classmethod
    def add_kand_time_diff(cls, td):
        cls.kand_td_index = (cls.kand_td_index + 1) % len(cls.kand_time_diffs)
        cls.kand_time_diffs[cls.kand_td_index] = td
        cls.kand_avg_time = sum(cls.kand_time_diffs) / len(cls.kand_time_diffs)