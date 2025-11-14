from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from condition.values import unquote, val_to_int64_slice
from .base_handler import ValueHandler


class IntHandler(ValueHandler):
    """整数值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.INT

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = c.field

        if c.op in [Op.EQ, Op.LT, Op.LTE, Op.GT, Op.GTE]:
            result.append(field_expr)
            result.append(c.op.code())
            result.append(unquote(c.val))
        elif c.op == Op.IN:
            result.append(field_expr)
            result.append(" ")
            result.append(c.op.code())
            result.append(" ")
            self._write_int_slice_for_expr(result, c.val)
        elif c.op == Op.CONTAINS_ANY:
            result.append("ContainsAny(")
            result.append(field_expr)
            result.append(", ")
            self._write_int_slice_for_expr(result, c.val)
            result.append(", ")
            result.append(str(c.keyword).lower())
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:
        suggestions = []

        try:
            if condition.op == Op.EQ:
                suggestions.append(f"将值改为 {condition.val}")
            elif condition.op == Op.CONTAINS_ANY:
                expected_values = val_to_int64_slice(condition.val)
                suggestions.append(f"将值改为 {expected_values} 中的任意一个")
            elif condition.op in [Op.GT, Op.GTE, Op.LT, Op.LTE]:
                expected_val = int(condition.val)
                suggestions.append(f"调整值以满足 {condition.op.code()} {expected_val}")
        except Exception:
            suggestions.append("检查条件配置是否正确")

        return suggestions

    def _write_int_slice_for_expr(self, result: List[str], val: str) -> None:
        """写入整数切片到表达式"""
        int_slice = val_to_int64_slice(val)
        result.append("[")
        for i, e in enumerate(int_slice):
            if i > 0:
                result.append(",")
            result.append(str(e))
        result.append("]")
































