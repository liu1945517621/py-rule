from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from condition.values import unquote
from .base_handler import ValueHandler


class StringHandler(ValueHandler):
    """字符串值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.STRING

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = self._get_field_expression(c.field)

        if c.op in [Op.EQ, Op.LT, Op.LTE, Op.GT, Op.GTE]:
            result.append(field_expr)
            result.append(c.op.code())
            result.append("\"")
            result.append(unquote(c.val))
            result.append("\"")
        elif c.op == Op.IN:
            result.append(field_expr)
            result.append(" ")
            result.append(c.op.code())
            result.append(" ")
            result.append(c.val)
        elif c.op == Op.CONTAINS_ANY:
            result.append("ContainsAny(")
            result.append(field_expr)
            result.append(", ")
            result.append(c.val)
            result.append(", ")
            result.append(str(c.keyword).lower())
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []