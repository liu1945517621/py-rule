from abc import ABC, abstractmethod
from typing import List, Any
from condition.var import ValType
from condition.condition import Condition


class ValueHandler(ABC):
    """值类型处理器抽象基类"""

    @abstractmethod
    def supports(self, val_type: ValType) -> bool:
        """判断是否支持该值类型"""
        pass

    @abstractmethod
    def build_expression(self, c: Condition, result: List[str]) -> None:
        """构建表达式"""
        pass

    @abstractmethod
    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:
        """生成修改建议"""
        pass

    def _get_field_expression(self, field: str) -> str:
        """获取字段表达式，处理方法调用"""
        # if field.endswith("()"):
        #     return field[:-2]
        return field
