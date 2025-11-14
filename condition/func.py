from datetime import datetime, date
from typing import Callable, Any, Tuple


def add_period_func() -> Tuple[str, Callable]:
    """用于给expr.Function添加AddPeriod方法"""
    # 用于给日期 / 时间增加指定周期（秒、分、时、天）
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
