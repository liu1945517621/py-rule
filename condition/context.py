import threading
from typing import Any, Optional


class Context:
    """上下文类，用于存储键值对数据"""

    def __init__(self, ctx: Optional[Any] = None):
        self._kv = {}
        self._lock = threading.RLock()
        self._ctx = ctx

    @classmethod
    def new_context(cls) -> 'Context':
        """创建新的上下文"""
        return cls()

    @classmethod
    def with_context(cls, ctx: Any) -> 'Context':
        """基于现有上下文创建"""
        return cls(ctx)

    def set(self, key: str, value: Any) -> None:
        """设置键值对"""
        with self._lock:
            self._kv[key] = value

    def get(self, key: str) -> (Any, bool):
        """获取值"""
        with self._lock:
            if key in self._kv:
                return self._kv[key], True
            if self._ctx:
                # 简化实现，实际可能需要从ctx中获取
                pass
            return None, False

    def get_string(self, key: str) -> (str, bool):
        """获取字符串值"""
        value, exists = self.get(key)
        if exists and value is not None:
            return str(value), True
        return "", False

    def get_bool(self, key: str) -> (bool, bool):
        """获取布尔值"""
        value, exists = self.get(key)
        if exists and value is not None:
            return bool(value), True
        return False, False

    def get_int64(self, key: str) -> (int, bool):
        """获取int64值"""
        value, exists = self.get(key)
        if exists and value is not None:
            try:
                return int(value), True
            except (ValueError, TypeError):
                pass
        return 0, False
