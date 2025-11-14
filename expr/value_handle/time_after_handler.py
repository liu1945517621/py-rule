from typing import List, Any
from condition.op import  Op
from condition.var import ValType
from condition.condition import Condition
from condition.values import unquote
from .base_handler import ValueHandler


class TimeAfterHandler(ValueHandler):
    """之后时间值处理器"""

    def supports(self, val_type: ValType) -> bool:
        return val_type == ValType.TIME_AFTER

    def build_expression(self, c: Condition, result: List[str]) -> None:
        # 验证 period_unit 是否有效
        # 有效的 period_unit 值：2(秒), 3(分), 4(小时), 5(天)
        # 0 表示无效值（UnitNone）
        ALL_PERIOD_UNITS = [2, 3, 4, 5]
        UNIT_NONE = 0
        
        if c.period_unit == UNIT_NONE or c.period_unit not in ALL_PERIOD_UNITS:
            raise ValueError(f"invalid condition:unsupported period unit {c.period_unit}")
        
        field_expr = self._get_field_expression(c.field)

        if c.op in [Op.EQ, Op.LT, Op.LTE, Op.GT, Op.GTE]:
            result.append(field_expr)
            result.append(c.op.code())
            result.append(f"AddPeriod(now(), {unquote(c.val)}, {c.period_unit})")
        else:
            raise ValueError(f"invalid condition:unsupported op {c.op} for val type {c.val_type.text()}")

    def generate_suggestions(self, condition: Condition, actual_value: Any) -> List[str]:

        return []