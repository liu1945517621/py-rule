import json
from typing import List, Union


def unquote(val: str) -> str:
    """去除引号"""
    if not val:
        return val
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    return val


def val_to_int64_slice(val: str) -> List[int]:
    """将值转换为int64切片"""
    val = unquote(val)
    if not val:
        return []

    try:
        # 尝试解析为JSON数组
        if val.startswith('[') and val.endswith(']'):
            data = json.loads(val)
            if isinstance(data, list):
                return [int(item) for item in data]
        else:
            # 单个值
            return [int(val)]
    except (json.JSONDecodeError, ValueError):
        # 尝试逗号分隔
        try:
            items = val.split(',')
            return [int(item.strip()) for item in items if item.strip()]
        except ValueError:
            pass

    return []


def val_to_string_slice(val: str) -> List[str]:
    """将值转换为字符串切片"""
    val = unquote(val)
    if not val:
        return []

    try:
        # 尝试解析为JSON数组
        if val.startswith('[') and val.endswith(']'):
            data = json.loads(val)
            if isinstance(data, list):
                return [str(item) for item in data]
        else:
            # 单个值
            return [val]
    except json.JSONDecodeError:
        # 尝试逗号分隔
        items = val.split(',')
        return [item.strip() for item in items if item.strip()]

    return []
