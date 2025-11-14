from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from condition.values import unquote, val_to_string_slice
from .base_handler import ValueHandler


class VarHandler(ValueHandler):
    """变量值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.VAR

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = self._get_field_expression(c.field)

        if c.op in [Op.EQ, Op.LT, Op.LTE, Op.GT, Op.GTE]:
            result.append(field_expr)
            result.append(c.op.code())
            result.append(unquote(c.val))
        elif c.op == Op.IN:
            result.append(field_expr)
            result.append(" ")
            result.append(c.op.code())
            result.append(" ")
            self._write_var_slice_for_expr(result, c.val)
        elif c.op == Op.CONTAINS_ANY:
            result.append("ContainsAny(")
            result.append(field_expr)
            result.append(", ")
            self._write_var_slice_for_expr(result, c.val)
            result.append(", ")
            result.append(str(c.keyword).lower())
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def _write_var_slice_for_expr(self, result: List[str], val: str) -> None:
        """写入变量切片到表达式"""
        try:
            str_slice = val_to_string_slice(val)
            result.append("[")
            for i, e in enumerate(str_slice):
                if i > 0:
                    result.append(",")
                result.append(e)
            result.append("]")
        except:
            result.append(val)

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []