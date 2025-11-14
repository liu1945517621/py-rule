from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from .base_handler import ValueHandler


class TimeHandler(ValueHandler):
    """时间值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.TIME

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = self._get_field_expression(c.field)

        if c.op in [Op.EQ, Op.LT, Op.LTE, Op.GT, Op.GTE]:
            result.append(field_expr)
            result.append(c.op.code())
            result.append("date(")
            if not c.val.startswith("\""):
                result.append("\"")
            result.append(c.val)
            if not c.val.endswith("\""):
                result.append("\"")
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []