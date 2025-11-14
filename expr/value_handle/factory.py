from typing import List, Optional, Any

from condition import Condition
from condition.var import ValType
from .base_handler import ValueHandler
from .int_handler import IntHandler
from .string_handler import StringHandler
from .float_handler import FloatHandler
from .bool_handler import BoolHandler
from .time_handler import TimeHandler
from .time_before_handler import TimeBeforeHandler
from .time_after_handler import TimeAfterHandler
from .var_handler import VarHandler
from .group_handler import GroupHandler
from .bi_crowd_handler import BICrowdHandler


class HandlerFactory:
    """处理器工厂"""

    def __init__(self):
        self._handlers: List[ValueHandler] = [
            IntHandler(),
            StringHandler(),
            FloatHandler(),
            BoolHandler(),
            TimeHandler(),
            TimeBeforeHandler(),
            TimeAfterHandler(),
            VarHandler(),
            GroupHandler(),
            BICrowdHandler()
        ]

    def get_handler(self, val_type: ValType) -> Optional[ValueHandler]:
        """根据值类型获取对应的处理器"""
        for handler in self._handlers:
            if handler.supports(val_type):
                return handler
        return None

    def register_handler(self, handler: ValueHandler) -> None:
        """注册新的处理器"""
        self._handlers.append(handler)

    def get_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:
        """根据条件和实际值生成建议"""
        handler = self.get_handler(condition.val_type)
        if handler:
            return handler.generate_suggestions(condition, actual_value)
        return ["未知类型，无法提供具体建议"]