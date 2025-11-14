from typing import List, Callable, Optional, Tuple, Dict, Any
from .condition import Condition


class ValAndType:
    """值和类型"""

    def __init__(self, val: str, val_type: str):
        self.val = val
        self.val_type = val_type


class ConvertMapping:
    """转换映射"""

    def __init__(self, source_field: str, target_field: str,
                 val_mappings: Dict[ValAndType, ValAndType] = None):
        self.source_field = source_field
        self.target_field = target_field
        self.val_mappings = val_mappings or {}


class ConvertOption:
    """转换选项"""

    def __init__(self,
                 mappings: List[ConvertMapping] = None,
                 converters: List[Callable] = None,
                 on_convert_fn: Callable = None):
        self.mappings = mappings or []
        self.converters = converters or []
        self.on_convert_fn = on_convert_fn


def join_converters(*converters: Callable) -> Callable:
    """连接多个转换器"""

    def converter(src: Condition) -> Tuple[Condition, bool, Exception]:
        if not converters:
            return src, False, None

        dst = src
        converted = False

        for conv in converters:
            inner_dst, inner_converted, inner_err = conv(dst)
            if inner_err:
                return dst, converted, inner_err
            if inner_converted:
                converted = True
                dst = inner_dst

        return dst, converted, None

    return converter


def convert_condition(c: Condition, opt: ConvertOption) -> Tuple[Condition, Exception]:
    """转换条件"""
    if not c.is_join():
        return _convert_for_single(c, opt)

    dst = c.clone()
    dst.conditions = []

    for child in c.conditions:
        child_dst, inner_err = convert_condition(child, opt)
        if inner_err:
            return None, inner_err
        dst.conditions.append(child_dst)

    return dst, None


def _convert_for_single(c: Condition, opt: ConvertOption) -> Tuple[Condition, Exception]:
    """转换单个条件"""
    dst = c.clone()

    # 应用字段映射
    for mapping in opt.mappings:
        if mapping.source_field == c.field:
            dst.field = mapping.target_field
            # 应用值映射
            if mapping.val_mappings:
                source_val_type = ValAndType(c.val, c.val_type.value if c.val_type else "")
                if source_val_type in mapping.val_mappings:
                    target_val_type = mapping.val_mappings[source_val_type]
                    dst.val = target_val_type.val
                    # 这里应该设置正确的ValType，简化处理
            break

    return dst, None
