import copy
from typing import List, Optional, Dict

from condition.op import Op, JoinOp
from condition.var import ValType


class Condition:
    def __init__(self,
                 field: str = "",
                 op: Op = None,
                 val: str = "",
                 val_type: ValType = None,
                 join_op: JoinOp = None,
                 conditions: List['Condition'] = None,
                 required: bool = False,
                 source: Optional['Condition'] = None,
                 hints: Dict[str, str] = None,
                 keyword: bool = False,
                 period_unit: int = 0):
        self.field = field
        self.op = op
        self.val = val
        self.val_type = val_type
        self.join_op = join_op
        self.conditions = conditions or []
        self.required = required
        self.source = source
        self.hints = hints or {}
        self.keyword = keyword
        self.period_unit = period_unit

    def is_empty(self) -> bool:
        """判断条件是否为空"""
        return (not self.field and not self.op and not self.val and
                not self.join_op and not self.conditions)

    def clone(self) -> 'Condition':
        """克隆条件"""
        return copy.deepcopy(self)

    def equals(self, other: 'Condition') -> bool:
        """判断两个条件是否相等"""
        if not other:
            return False
        return (self.field == other.field and
                self.op == other.op and
                self.val == other.val and
                self.val_type == other.val_type and
                self.join_op == other.join_op and
                self.required == other.required and
                self.keyword == other.keyword and
                self.period_unit == other.period_unit and
                len(self.conditions) == len(other.conditions) and
                all(c1.equals(c2) for c1, c2 in zip(self.conditions, other.conditions)))

    def is_join(self) -> bool:
        """判断是否为组合条件"""
        return self.join_op is not None

    def is_always_true(self) -> bool:
        """判断是否恒为真"""
        return (self.field == "1" and self.op == Op.EQ and
                self.val == "1" and self.val_type == ValType.INT)

    def is_always_false(self) -> bool:
        """判断是否恒为假"""
        return (self.field == "1" and self.op == Op.EQ and
                self.val == "2" and self.val_type == ValType.INT)

    def not_(self) -> 'Condition':
        """取反条件"""
        if self.is_join() and self.join_op == JoinOp.NOT:
            if len(self.conditions) == 1:
                return self.conditions[0].clone()

        not_cond = Condition()
        not_cond.join_op = JoinOp.NOT
        not_cond.conditions = [self.clone()]
        return not_cond

    def simplify(self) -> 'Condition':
        """简化条件"""
        if self.is_join() and self.join_op == JoinOp.NOT:
            if len(self.conditions) == 1:
                child = self.conditions[0]
                if child.is_join() and child.join_op == JoinOp.NOT:
                    return child.conditions[0].simplify()
        return self

    def transform_forward(self) -> 'Condition':
        """前向转换条件"""
        if self.op and self.op.forward_op():
            not_cond = Condition()
            not_cond.join_op = JoinOp.NOT
            new_cond = Condition(self.field, self.op.forward_op(), self.val, self.val_type)
            not_cond.conditions = [new_cond]
            return not_cond
        return self

    def all_fields(self) -> List[str]:
        """获取所有字段"""
        if not self.is_join():
            return [self.field] if self.field else []

        fields = []
        for child in self.conditions:
            fields.extend(child.all_fields())
        return list(set(fields))

    def contains_fields(self, field: str) -> bool:
        """判断是否包含字段"""
        return field in self.all_fields()

    def expend_not(self) -> ('Condition', bool):
        """展开NOT操作"""
        # 简化实现
        return self.clone(), False


# 预定义的恒真和恒假条件
_always_true = Condition("1", Op.EQ, "1", ValType.INT)
_always_false = Condition("1", Op.EQ, "2", ValType.INT)


def And(*conditions: Condition) -> Condition:
    """创建AND条件"""
    copied_conditions = [cond.clone() for cond in conditions if cond and not cond.is_empty()]
    result = Condition()
    result.join_op = JoinOp.AND
    result.conditions = copied_conditions
    return result


def Or(*conditions: Condition) -> Condition:
    """创建OR条件"""
    copied_conditions = [cond.clone() for cond in conditions if cond and not cond.is_empty()]
    result = Condition()
    result.join_op = JoinOp.OR
    result.conditions = copied_conditions
    return result


def Not(cond: Condition) -> Condition:
    """创建NOT条件"""
    if not cond or cond.is_empty():
        return cond
    return cond.not_()


def IsEmpty(c: Condition) -> bool:
    """判断条件是否为空"""
    return c is None or c.is_empty()


def IsAlwaysTrue(c: Condition) -> bool:
    """判断是否恒为真"""
    return c is not None and c.is_always_true()


def IsAlwaysFalse(c: Condition) -> bool:
    """判断是否恒为假"""
    return c is not None and c.is_always_false()


def NewAlwaysTrue() -> Condition:
    """创建新的恒真条件"""
    return _always_true.clone()


def NewAlwaysFalse() -> Condition:
    """创建新的恒假条件"""
    return _always_false.clone()
