from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from condition.values import val_to_int64_slice
from .base_handler import ValueHandler


class BICrowdHandler(ValueHandler):
    """BI人群值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.BI_CROWD

    def build_expression(self, c: Condition, result: List[str]) -> None:
        field_expr = self._get_field_expression(c.field)

        if c.op == Op.IN:
            result.append("InBICrowd(Context, ")
            result.append(field_expr)
            result.append(", ")
            self._write_int_slice_for_expr(result, c.val)
            result.append(")")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def _write_int_slice_for_expr(self, result: List[str], val: str) -> None:
        """写入整数切片到表达式"""
        int_slice = val_to_int64_slice(val)
        result.append("[")
        for i, e in enumerate(int_slice):
            if i > 0:
                result.append(",")
            result.append(str(e))
        result.append("]")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []