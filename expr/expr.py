from typing import List
from condition.condition import Condition, JoinOp
from .value_handle.factory import HandlerFactory


class ExpressionBuilder:
    """表达式构建器"""

    def __init__(self):
        self._handler_factory = HandlerFactory()

    def build_expression(self, c: Condition) -> str:
        """构建表达式字符串"""
        # 简化条件
        target = c.transform_forward()
        target = target.simplify()

        result = []
        self._build_expr(target, result)
        return ''.join(result)

    def _build_expr(self, c: Condition, result: List[str]) -> None:
        """构建表达式字符串"""
        if c.is_join():
            self._build_join_expression(c, result)
            return

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
                if field_name.endswith("()"):
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
            self._build_expr(child, result)
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

    def build_expressions_with_or_split(self, c: Condition) -> List[str]:
        """
        构建表达式，当遇到 OR 操作符时进行拆分，返回多个表达式

        Args:
            c: Condition 条件对象

        Returns:
            List[str]: 拆分后的表达式列表
        """
        # 转正向表达式
        target = c.transform_forward()
        # 简化条件
        target = target.simplify()

        return self._recursive_split_or(target)

    def _recursive_split_or(self, c: Condition) -> List[str]:
        """
        递归拆分OR表达式
        """
        if not c.is_join():
            # 叶子节点
            result = []
            self._build_expr(c, result)
            return [''.join(result)]

        if c.join_op != JoinOp.AND:
            # 对于OR和NOT操作符，直接递归处理
            if c.join_op == JoinOp.OR:
                expressions = []
                for child in c.conditions:
                    expressions.extend(self._recursive_split_or(child))
                return expressions
            else:  # NOT操作符
                result = []
                self._build_expr(c, result)
                return [''.join(result)]

        # AND操作符处理
        # 检查是否有OR子条件需要拆分
        all_splits = []
        for child in c.conditions:
            child_splits = self._recursive_split_or(child)
            all_splits.append(child_splits)

        # 笛卡尔积组合
        from itertools import product
        result = []
        for combination in product(*all_splits):
            # 构建新的AND表达式
            expr_parts = []
            for i, part in enumerate(combination):
                if i > 0:
                    expr_parts.append(JoinOp.AND.code())
                expr_parts.append(part)

            final_expr = f"({''.join(expr_parts)})" if len(expr_parts) > 1 else expr_parts[0]
            result.append(final_expr)

        return result


# 全局表达式构建器实例
_builder = ExpressionBuilder()


def expr(c: Condition) -> str:
    """生成expr表达式"""
    return _builder.build_expression(c)

def expr_with_or_split(c: Condition) -> list[str]:
    """生成expr表达式"""
    return _builder.build_expressions_with_or_split(c)
