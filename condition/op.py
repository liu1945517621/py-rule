from enum import Enum


class Op(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS_ANY = "contains_any"
    NOT_CONTAINS_ANY = "not_contains_any"

    def code(self) -> str:
        return self.value

    def text(self) -> str:
        texts = {
            Op.EQ: "等于",
            Op.NE: "不等于",
            Op.LT: "小于",
            Op.LTE: "小于等于",
            Op.GT: "大于",
            Op.GTE: "大于等于",
            Op.IN: "包含于",
            Op.NOT_IN: "不包含于",
            Op.CONTAINS_ANY: "包含",
            Op.NOT_CONTAINS_ANY: "不包含"
        }
        return texts.get(self, "未知")

    def forward_op(self):
        """对应正向操作符"""
        forward_map = {
            Op.NE: Op.EQ,
            Op.NOT_IN: Op.IN,
            Op.NOT_CONTAINS_ANY: Op.CONTAINS_ANY
        }
        return forward_map.get(self)


class JoinOp(Enum):
    AND = "and"
    OR = "or"
    NOT = "not"

    def code(self) -> str:
        return self.value

    def text(self) -> str:
        texts = {
            JoinOp.AND: "且",
            JoinOp.OR: "或",
            JoinOp.NOT: "非"
        }
        return texts.get(self, "未知")


# 定义所有操作符常量
OpGt = Op.GT
OpGte = Op.GTE
OpLt = Op.LT
OpLte = Op.LTE
OpEq = Op.EQ
OpNe = Op.NE
OpIn = Op.IN
OpNotIn = Op.NOT_IN
OpContainsAny = Op.CONTAINS_ANY
OpNotContainsAny = Op.NOT_CONTAINS_ANY

JoinOpAnd = JoinOp.AND
JoinOpOr = JoinOp.OR
JoinOpNot = JoinOp.NOT

# 所有操作符列表
AllOps = [
    OpGt,
    OpGte,
    OpLt,
    OpLte,
    OpEq,
    OpNe,
    OpIn,
    OpNotIn,
    OpContainsAny,
    OpNotContainsAny,
]
