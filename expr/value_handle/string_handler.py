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
        """生成字符串类型的建议"""
        suggestions = []

        if actual_value is None:
            suggestions.append("字段值为空，请检查数据源")
            return suggestions

        actual_str = str(actual_value) if actual_value is not None else ""
        expected_str = unquote(condition.val) if condition.val else ""

        # 根据不同的操作符生成相应的建议
        if condition.op == Op.EQ:
            suggestions.append(f"期望值: '{expected_str}', 实际值: '{actual_str}'")
            if len(actual_str) != len(expected_str):
                suggestions.append(f"长度不匹配，期望长度: {len(expected_str)}, 实际长度: {len(actual_str)}")

        elif condition.op == Op.CONTAINS_ANY:
            # 对于 CONTAINS_ANY 操作，检查实际值是否包含任意期望的子串
            if hasattr(condition, 'val_list'):
                expected_values = condition.val_list
            else:
                # 解析 val 字符串为列表
                try:
                    expected_values = eval(condition.val) if condition.val else []
                except:
                    expected_values = [condition.val] if condition.val else []

            matched = [val for val in expected_values if val in actual_str]
            unmatched = [val for val in expected_values if val not in actual_str]

            if matched:
                suggestions.append(f"已匹配的值: {matched}")
            if unmatched:
                suggestions.append(f"未匹配的值: {unmatched}")

        elif condition.op == Op.IN:
            try:
                expected_list = eval(condition.val) if condition.val else []
            except:
                expected_list = [condition.val] if condition.val else []

            if actual_str not in expected_list:
                suggestions.append(f"值 '{actual_str}' 不在允许的列表 {expected_list} 中")
            else:
                suggestions.append(f"值 '{actual_str}' 在允许的列表中")

        elif condition.op in [Op.LT, Op.LTE, Op.GT, Op.GTE]:
            suggestions.append(f"比较操作失败: '{actual_str}' 与 '{expected_str}'")
            try:
                # 尝试数值比较
                actual_num = float(actual_str)
                expected_num = float(expected_str)
                if actual_num < expected_num:
                    suggestions.append(f"数值比较结果: {actual_num} < {expected_num}")
                elif actual_num > expected_num:
                    suggestions.append(f"数值比较结果: {actual_num} > {expected_num}")
                else:
                    suggestions.append(f"数值相等: {actual_num} == {expected_num}")
            except ValueError:
                suggestions.append("无法进行数值比较，字符串不能转换为数字")

        return suggestions
