from condition.condition import Condition, Op, ValType, JoinOp
from expr.expr import expr, expr_with_or_split
from runtime import DiagnosticEvaluator
from runtime.DiagnosticEvaluator import print_diagnostics


class User:
    def __init__(self, id: int, month: int, name: str):
        self.Id = id
        self.month = month
        self.name = name

    def Name(self) -> str:
        return self.name


async def main():
    # 构造条件 实际上这里是通过内容池的策略配置 json 转换而来
    # 构造一个 or 的条件
    #  ((Id==1) or (Name()=="A Mao")
    orCond = Condition()
    orCond.join_op = JoinOp.OR
    orCond.conditions = [
        Condition("Id", Op.EQ, "1", ValType.INT),
        Condition("Name()", Op.EQ, "A Mao", ValType.STRING)
    ]

    # 构造一个and 条件
    # (((Id == 1) or (Name() == "A Mao")) and (ContainsAny(month, [3, 7, 11], false)))
    cond = Condition()
    cond.join_op = JoinOp.AND
    cond.conditions = [
        orCond,
        Condition("month", Op.CONTAINS_ANY, "[3,7,11]", ValType.INT),
    ]

    # 转换为表达式
    expr_str = expr(cond)
    print(f"表达式: {expr_str}")

    expr_str_list = expr_with_or_split(cond)
    print(f"拆分OR的表达式: ")
    for expr_str1 in expr_str_list:
        print(f" {expr_str1}")

    # 创建用户对象
    user1 = User(1, 3,"A Mao")
    user2 = User(2, 1,"B Mao")

    # 获取自定义函数 ContainsAny 函数定义
    from condition.func import contains_any_func
    _, contains_any_fn = contains_any_func()

    # 准备执行环境，包含所需的自定义函数
    functions = {
        # 定义自定义函数 ContainsAny ， 可能还会有 AddPeriod
        "ContainsAny": contains_any_fn,
        # 标明go与python 的区别， 因为 python 的 false 和 go 的 false 不一样
        "false": False,
        "true": True,
    }

    print("")
    print(f"判断表达式: {expr_str} ")
    ##### 待分析的评估
    evaluator = DiagnosticEvaluator(functions)
    env1 = {"Id": user1.Id, "Name": user1.Name, "month": user1.month}
    result1,diagnostics1 = evaluator.evaluate_with_diagnostics(cond, env1)
    print(f"User1 Result result: {result1}")
    if not result1:
        print_diagnostics(diagnostics1)



    # 为 user2 评估
    env2 = {"Id": user2.Id, "Name": user2.Name, "month": user2.month}
    result2,diagnostics2 = evaluator.evaluate_with_diagnostics(cond, env2)
    print(f"User2 result: {result2}")
    if not result2:
        print_diagnostics(diagnostics2)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
