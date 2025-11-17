from typing import List, Any
import json
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from .base_handler import ValueHandler


class GroupHandler(ValueHandler):
    """群组值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.GROUP

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = self._get_field_expression(c.field)

        if c.op == Op.IN:
            result.append("InGroups(Context, ")
            result.append(field_expr)
            result.append(", ")
            values = json.loads(c.val)
            for i, value in enumerate(values):
                if i > 0:
                    result.append(", ")
                result.append("[")
                result.append(value)
                result.append("]")
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []