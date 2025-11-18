# 修改后的 selector.py
from typing import List, Set, Callable, Optional
from .condition import Condition

class Selector:
    """选择器接口，用于筛选字段"""

    def is_empty(self) -> bool:
        """判断选择器是否为空"""
        raise NotImplementedError

    def match(self, c: Condition) -> bool:
        """匹配条件"""
        raise NotImplementedError

class DefaultSelector(Selector):
    """默认选择器实现"""

    def __init__(self):
        self._include: List[str] = []
        self._exclude: List[str] = []
        self._predicate: Optional[Callable[[Condition], bool]] = None

    @classmethod
    def new_selector(cls) -> 'DefaultSelector':
        """创建新的选择器"""
        return cls()

    def with_include(self, *fields: str) -> 'DefaultSelector':
        """添加包含字段"""
        self._include.extend(fields)
        return self

    def with_exclude(self, *fields: str) -> 'DefaultSelector':
        """添加排除字段"""
        self._exclude.extend(fields)
        return self

    def with_predicate(self, predicate: Callable[[Condition], bool]) -> 'DefaultSelector':
        """添加谓词函数"""
        self._predicate = predicate
        return self

    def is_empty(self) -> bool:
        """判断选择器是否为空"""
        return len(self._include) == 0 and len(self._exclude) == 0 and self._predicate is None

    def match(self, c: Condition) -> bool:
        """匹配条件"""
        # 检查是否包含指定字段
        include_match = len(self._include) > 0 and c.contains_fields(*self._include)

        # 检查是否排除指定字段
        exclude_match = len(self._exclude) > 0 and not c.contains_fields(*self._exclude)

        # 检查谓词函数
        predicate_match = self._predicate is not None and self._predicate(c)

        return include_match or exclude_match or predicate_match

def join_selector(*selectors: Selector) -> Selector:
    """连接多个选择器"""
    if len(selectors) == 0:
        return DefaultSelector()
    if len(selectors) == 1:
        return selectors[0]
    return JoinedSelector(selectors)

class JoinedSelector(Selector):
    """连接选择器实现"""

    def __init__(self, selectors: List[Selector]):
        self._selectors = selectors

    def is_empty(self) -> bool:
        """判断选择器是否为空"""
        for selector in self._selectors:
            if not selector.is_empty():
                return False
        return True

    def match(self, c: Condition) -> bool:
        """匹配条件"""
        for selector in self._selectors:
            if selector.match(c):
                return True
        return False

def not_selector(selector: Selector) -> Selector:
    """取反选择器"""
    if selector.is_empty():
        return DefaultSelector().with_predicate(lambda c: True)

    return DefaultSelector().with_predicate(lambda c: not selector.match(c))
