from typing import List, Optional, Tuple, Any
from .var import ValType
import json

class MetaValue:
    """元数据值"""
    def __init__(self, val: str = "", val_type: ValType = None,
                 name: str = "", val_dic: str = "", period_unit: int = 0):
        self.val = val
        self.val_type = val_type
        self.name = name
        self.val_dic = val_dic
        self.period_unit = period_unit  # 当字段类型为时间，值为相对时间时，相对时间的单位

class Meta:
    """元数据"""
    def __init__(self, field: str = "", name: str = "",
                 support_val_types: List['ValTypeName'] = None,
                 support_ops: List['Op'] = None,
                 support_values: List[MetaValue] = None,
                 val_dic: str = "", keyword: bool = False,
                 required: bool = False):
        self.field = field
        self.name = name
        self.support_val_types = support_val_types or []  # 支持的值类型
        self.support_ops = support_ops or []  # 支持的操作符
        self.support_values = support_values or []  # 支持的值，有值时，用户选择输入
        self.val_dic = val_dic  # 值字典，如果用值是，通过该值，请求本接口获取值字典
        self.keyword = keyword  # 是否允许使用关键词方式进行匹配，ContainsAny操作使用
        self.required = required  # 值是否必须，当在非类型操作符时，会需要额外验证是否零值

class ValTypeName:
    """值类型名称"""
    def __init__(self, id: ValType = None, name: str = ""):
        self.id = id  # 值类型
        self.name = name  # 值类型名


def meta_value_from_group_providers(providers: List[Any]) -> tuple[list[Any], None]:
    """
    从多个group provider创建MetaValue列表

    Args:
        providers: group provider列表

    Returns:
        (meta_values, error) 元组
    """
    meta_values = []

    for provider in providers:
        provider_meta_values, inner_err = meta_value_from_group_provider(provider)
        if inner_err:
            # 继续处理其他provider，但记录错误
            print(f"Warning: {inner_err}")
            continue
        meta_values.extend(provider_meta_values)

    return meta_values, None


def meta_value_from_group_provider(provider: Any) -> tuple[list[Any], Exception] | tuple[list[Any], None]:
    """
    从单个group provider创建MetaValue列表

    Args:
        provider: group provider对象

    Returns:
        (meta_values, error) 元组
    """
    meta_values = []

    try:
        groups = provider.list()  # 假设provider有list方法
    except Exception as e:
        return [], e

    for group in groups:
        meta_value, inner_err = meta_value_from_group(group)
        if inner_err:
            # 继续处理其他group，但记录错误
            print(f"Warning: {inner_err}")
            continue
        if meta_value:
            meta_values.append(meta_value)

    return meta_values, None


def meta_value_from_group(group: Any) -> tuple[None, None] | tuple[MetaValue, None] | tuple[None, Exception]:
    """
    从单个group创建MetaValue

    Args:
        group: group对象

    Returns:
        (meta_value, error) 元组
    """
    # 检查group数据源是否存在
    if not hasattr(group, 'data_source') or group.data_source is None:
        return None, None

    # 构建名称
    name = group.name
    if hasattr(group, 'status') and hasattr(group, 'status_disabled'):
        if group.status == group.status_disabled:
            name = name + "(已失效)"

    # 根据数据源类型处理
    try:
        data_source_type = group.data_source.type
    except AttributeError:
        return None, None

    if hasattr(group, 'data_source_type_redis'):
        expected_type = group.data_source_type_redis
    else:
        # 假设redis类型为字符串"redis"
        expected_type = "redis"

    if data_source_type == expected_type:
        try:
            data_source = group.data_source
            meta_value = MetaValue(
                val=json.dumps(data_source.key_format),  # 使用json.dumps模拟Go中的fmt.Sprintf("\"%s\"", ...)
                val_type=ValType.GROUP,  # 假设ValType有GROUP枚举值
                name=name
            )
            return meta_value, None
        except Exception as e:
            return None, e

    return None, None