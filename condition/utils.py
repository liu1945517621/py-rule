# 工具函数集合

def is_collection(obj) -> bool:
    """判断对象是否为集合类型"""
    return hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes))

def is_empty(obj) -> bool:
    """判断对象是否为空"""
    if obj is None:
        return True
    if is_collection(obj):
        return len(obj) == 0
    return False
