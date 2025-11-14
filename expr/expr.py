from typing import List
from condition.condition import Condition, JoinOp
from .value_handle.factory import HandlerFactory


class ExpressionBuilder:
    """表达式构建器"""

    def __init__(self):
        self._handler_factory = HandlerFactory()

    def build_expression(self, c: Condition) -> str:
        """构建表达式字符串"""

        target = c.transform_forward()   # 正向转换条件
        target = target.simplify()       # 简化条件

        result = []
        self._build_expr(target, result)
        return ''.join(result)

    def _build_expr(self, c: Condition, result: List[str]) -> None:
        """递归构建表达式字符串"""
        # 判断是否为连接条件（包含子条件）
        if c.is_join():
            self._build_join_expression(c, result)
            return
        # 若为单个条件，检查必要字段（field/op/val）是否存在
        if not c.field or not c.op or not c.val:
            return

        self._build_single_expression(c, result)

    def _build_join_expression(self, c: Condition, result: List[str]) -> None:
        """构建连接表达式"""
        if c.join_op == JoinOp.NOT:
            if len(c.conditions) != 1:
                raise ValueError("invalid condition:not join condition should have only one child")

            if c.required:
                result.append("IsNotZero(")
                field_name = c.conditions[0].field
                if field_name.endswith("()"):  # 移除字段名后的()
                    field_name = field_name[:-2]
                result.append(field_name)
                result.append(")")
                result.append(JoinOp.AND.code())

            result.append(c.join_op.code())
            self._build_expr(c.conditions[0], result)
            return

        result.append("(")
        for i, child in enumerate(c.conditions):
            if i > 0:
                result.append(c.join_op.code())
            self._build_expr(child, result)  # 递归处理子条件
        result.append(")")

    def _build_single_expression(self, c: Condition, result: List[str]) -> None:
        """构建单个条件表达式"""
        result.append("(")

        # 获取对应的值类型处理器
        handler = self._handler_factory.get_handler(c.val_type)
        if handler:
            handler.build_expression(c, result)
        else:
            # 处理其他值类型或抛出异常
            self._build_default_expression(c, result)

        result.append(")")

    def _build_default_expression(self, c: Condition, result: List[str]) -> None:
        """默认表达式构建（处理未支持的值类型）"""
        raise ValueError(f"Unsupported value type: {c.val_type}")


# 全局表达式构建器实例
_builder = ExpressionBuilder()


def expr(c: Condition) -> str:
    """生成expr表达式"""
    return _builder.build_expression(c)
