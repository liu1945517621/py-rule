from datetime import datetime, date
from typing import Callable, List, Tuple, Any, Union, Optional, Dict
import redis

import group
from . import InGrouper
from .context import Context
import threading
from concurrent.futures import ThreadPoolExecutor
import logging


def add_period_func() -> Tuple[str, Callable]:
    """用于给expr.Function添加AddPeriod方法"""

    def fn(*params) -> Any:
        if len(params) != 3:
            raise ValueError("AddPeriod must input 3 params")

        now = params[0]
        if not isinstance(now, (datetime, date)):
            raise ValueError("AddPeriod param[0] must be datetime or date")

        try:
            duration = int(params[1])
        except (ValueError, TypeError):
            raise ValueError("AddPeriod param[1] must be int")

        try:
            unit_int = int(params[2])
        except (ValueError, TypeError):
            raise ValueError("AddPeriod param[2] must be int")

        # 简化实现，实际应该根据unit_int进行不同的时间计算
        # 这里只做一个示例实现
        if isinstance(now, datetime):
            # 根据unit_int进行不同的时间操作
            if unit_int == 2:  # 秒
                return now.replace(second=now.second + duration)
            elif unit_int == 3:  # 分
                return now.replace(minute=now.minute + duration)
            elif unit_int == 4:  # 小时
                return now.replace(hour=now.hour + duration)
            elif unit_int == 5:  # 天
                return now.replace(day=now.day + duration)

        return now

    return "AddPeriod", fn


def today_func() -> Tuple[str, Callable]:
    """用于给expr.Function添加Today()方法"""

    def fn(*params) -> Any:
        now = datetime.now()
        return datetime(now.year, now.month, now.day)

    return "Today", fn


def contains_any_func() -> Tuple[str, Callable]:
    """用于给expr.Function添加ContainsAny方法"""

    def fn(*params) -> Any:
        if len(params) != 3:
            raise ValueError("ContainsAny must input 3 params")

        keyword = params[2]
        if not isinstance(keyword, bool):
            raise ValueError("ContainsAny params[2] must bool value")

        if keyword:
            return _contains_any_for_keyword(params)
        else:
            return _contains_any_for_not_keyword(params)

    return "ContainsAny", fn


def _contains_any_for_keyword(params) -> bool:
    """关键词模式的contains_any"""
    params0_str = str(params[0])
    param1_str_slice = list(params[1]) if hasattr(params[1], '__iter__') else [str(params[1])]

    for p1 in param1_str_slice:
        if str(p1) in params0_str:
            return True
    return False


def _contains_any_for_not_keyword(params) -> bool:
    """非关键词模式的contains_any"""
    param0_slice = list(params[0]) if hasattr(params[0], '__iter__') else [str(params[0])]
    param1_slice = list(params[1]) if hasattr(params[1], '__iter__') else [str(params[1])]

    param0_set = set(str(item) for item in param0_slice)
    param1_set = set(str(item) for item in param1_slice)

    return bool(param0_set.intersection(param1_set))


def is_not_zero_func() -> Tuple[str, Callable]:
    """用于给expr.Function添加IsNotZero方法"""

    def fn(*params) -> Any:
        if len(params) != 1:
            raise ValueError("IsNotZero must input 1 param")

        param = params[0]
        if param is None:
            return False

        # 检查是否为零值
        if isinstance(param, (int, float)):
            return param != 0
        elif isinstance(param, str):
            return len(param) > 0
        elif isinstance(param, (list, tuple)):
            return len(param) > 0
        elif isinstance(param, dict):
            return len(param) > 0
        else:
            return True

    return "IsNotZero", fn


def in_bi_crowd_func(key_prefix: str, redis_pool: redis.Redis) -> Tuple[str, callable]:
    """
    InBICrowdFunc 用于给 expr.Function 添加InBICrowd方法

    Args:
        key_prefix: Redis key前缀
        redis_pool: Redis连接池

    Returns:
        tuple: (函数名, 函数实现)
    """

    def in_bi_crowd_impl(*params: Any) -> Tuple[bool, Union[Exception, None]]:
        """
        InBICrowd函数实现

        Args:
            params[0]: condition.Context 上下文
            params[1]: userId 用户ID
            params[2]: crowd_ids 人群ID列表

        Returns:
            tuple: (结果, 错误信息)
        """
        result = False

        # 参数校验
        if len(params) != 3:
            return False, ValueError("InBICrowd must input 3 params")

        # 类型检查ctx是否为condition.Context实例
        ctx = params[0]
        if not hasattr(ctx, 'get_int') or not hasattr(ctx, 'set'):
            return False, ValueError("InBICrowd params[0] must be condition.Context")

        try:
            user_id = int(params[1])
        except (ValueError, TypeError) as e:
            return False, ValueError(f"InBICrowd params[1] must be int,{str(e)}")

        try:
            if isinstance(params[2], (list, tuple)):
                crowd_ids = [int(cid) for cid in params[2]]
            else:
                crowd_ids = [int(params[2])]
        except (ValueError, TypeError) as e:
            return False, ValueError(f"InBICrowd params[2] must be []int,{str(e)}")

        # 零值检查
        if len(crowd_ids) == 0 or user_id == 0:
            return result, None

        to_be_load_crowd_ids = []

        # 先从上下文尝试获取
        for crowd_id in crowd_ids:
            key = f"{key_prefix}{crowd_id}"
            val, ok = ctx.get_int(key)
            if ok:
                if val > 0:
                    return True, None
            else:
                to_be_load_crowd_ids.append(crowd_id)

        # 如果没有需要加载的数据，直接返回
        if len(to_be_load_crowd_ids) == 0:
            return result, None

        try:
            # 单个key的情况
            if len(to_be_load_crowd_ids) == 1:
                key = f"{key_prefix}{to_be_load_crowd_ids[0]}"
                bit = redis_pool.getbit(key, user_id)

                # 更新上下文
                ctx.set(key, bit)

                return bit > 0, None
            else:
                # 批量获取多个key
                pipe = redis_pool.pipeline()
                keys = []
                for crowd_id in to_be_load_crowd_ids:
                    key = f"{key_prefix}{crowd_id}"
                    keys.append(key)
                    pipe.getbit(key, user_id)

                pipeline_results = pipe.execute()

                # 处理结果
                for i, crowd_id in enumerate(to_be_load_crowd_ids):
                    bit = pipeline_results[i]
                    key = f"{key_prefix}{crowd_id}"

                    # 更新上下文
                    ctx.set(key, bit)

                    if bit > 0:
                        result = True

                return result, None

        except Exception as e:
            return False, e

    return "InBICrowd", in_bi_crowd_impl


def in_groups_func(in_groupers: List[InGrouper]) -> Tuple[str, Callable]:
    """用于给 expr.Function 添加InGroups方法"""

    def get_in_groups():
        return in_groupers

    return _in_groups_func(get_in_groups)


def _in_groups_func(get_in_groups: Callable[[], List[InGrouper]]) -> Tuple[str, Callable]:
    """
        InGroupsFunc的核心实现

        Args:
            params[0]: condition.Context 上下文
            params[1]: string 字段值的字符串
            params[2]: any 各group的参数,由各 InGrouper 实现
            params[3]: any 各group的参数,由各 InGrouper 实现
            params[n]: any 各group的参数,由各 InGrouper 实现
    """

    def fn(*params: Any) -> tuple[bool, ValueError] | tuple[bool, None] | tuple[bool, Exception] | tuple[bool, Any]:
        result = False
        if len(params) <= 2:
            return False, ValueError("InGroups must input more than 2 params")

        ctx = params[0]
        if not hasattr(ctx, 'get_int') or not hasattr(ctx, 'set'):
            return False, ValueError("InGroups params[0] must be condition.Context")

        field_val_str = str(params[1])

        # 如果为零值，不满足业务前提
        if field_val_str == "0" or field_val_str == "":
            return result, None

        in_groupers = get_in_groups()

        # 一个input仅由grouper一个处理
        input_index_to_match: Dict[int, bool] = {}
        grouper_index_to_inputs: Dict[int, List[List[Any]]] = {}

        for grouper_index, grouper in enumerate(in_groupers):
            grouper_inputs = []
            for input_index, input_param in enumerate(params[2:]):
                if input_index_to_match.get(input_index, False):
                    continue
                slice_input = list(input_param) if hasattr(input_param, '__iter__') else [input_param]
                if not grouper.match(ctx, field_val_str, slice_input):
                    continue
                input_index_to_match[input_index] = True
                grouper_inputs.append(slice_input)

            if len(grouper_inputs) > 0:
                grouper_index_to_inputs[grouper_index] = grouper_inputs

        if len(grouper_index_to_inputs) == 0:
            logging.debug("InGroupsFunc not match any InGroups")
            return result, None

        if len(grouper_index_to_inputs) == 1:
            for grouper_index, grouper_inputs in grouper_index_to_inputs.items():
                return in_groupers[grouper_index].in_groups(ctx, field_val_str, grouper_inputs)

        # 多个grouper并发处理
        def process_grouper(grouper_index: int, grouper_inputs: List[List[Any]]) -> Tuple[bool, Exception]:
            try:
                return in_groupers[grouper_index].in_groups(ctx, field_val_str, grouper_inputs)
            except Exception as e:
                return False, e

        with ThreadPoolExecutor(max_workers=len(grouper_index_to_inputs)) as executor:
            futures = []
            for grouper_index, grouper_inputs in grouper_index_to_inputs.items():
                future = executor.submit(process_grouper, grouper_index, grouper_inputs)
                futures.append(future)

            for future in futures:
                try:
                    inner_result, inner_err = future.result()
                    if inner_err:
                        return False, inner_err
                    if inner_result:
                        result = True
                except Exception as e:
                    return False, e

        return result, None

    return "InGroups", fn
