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
    # 构造条件
    # 构造一个or 的条件
    orCond = Condition()
    orCond.join_op = JoinOp.OR
    orCond.conditions = [
        Condition("Id", Op.EQ, "1", ValType.INT),
        Condition("Name()", Op.EQ, "A Mao", ValType.STRING)
    ]


    # 内容池的 json -> Condition()
    cond = Condition()
    cond.join_op = JoinOp.AND
    cond.conditions = [
        orCond,
        # Condition("Id", Op.EQ, "1", ValType.INT),
        # Condition("Name()", Op.EQ, "A Mao", ValType.STRING),
        Condition("month", Op.CONTAINS_ANY, "[3,7,11]", ValType.INT),
    ]

    # 转换为表达式
    expr_str = expr(cond)
    print(f"Expression: {expr_str}")


    expr_str_list = expr_with_or_split(cond)
    print(f"ExpressionNew: ")
    for expr_str in expr_str_list:
        print(f" {expr_str}")

    # 创建用户对象
    user1 = User(1, 6,"A Mao")
    user2 = User(2, 1,"A Mao")

    # 获取 ContainsAny 函数定义
    from condition.func import contains_any_func
    _, contains_any_fn = contains_any_func()

    # 准备执行环境，包含所需的自定义函数
    functions = {
        "ContainsAny": contains_any_fn,
        "false": False,  # 添加 Python 布尔值定义
        "true": True
    }

    # ((Id==1)and(Name()=="A Mao")and(ContainsAny(month, [3,7,11], false)))
    # ((Id==1)and(Name()=="A Mao")and(contains_any_fn(month, [3,7,11], False)))


    #### 简单评估是否满足
    # # 为 user1 评估
    # env1 = {"Id": user1.Id, "Name": user1.Name, "month": user1.month}
    # result1 = eval(expr_str, {"__builtins__": {}, **functions}, env1)
    # print(f"User1 result: {result1}")
    #
    # # 为 user2 评估
    # env2 = {"Id": user2.Id, "Name": user2.Name, "month": user2.month}
    # result2 = eval(expr_str, {"__builtins__": {}, **functions}, env2)
    # print(f"User2 result: {result2}")
    # 为 user1 评估


    ##### 待分析的评估
    # evaluator = DiagnosticEvaluator(functions)
    # env1 = {"Id": user1.Id, "Name": user1.Name, "month": user1.month}
    # result1,diagnostics1 = evaluator.evaluate_with_diagnostics(cond, env1)
    # print(f"User1 result: {result1}")
    # if not result1:
    #     print_diagnostics(diagnostics1)
    #
    # # 为 user2 评估
    # env2 = {"Id": user2.Id, "Name": user2.Name, "month": user2.month}
    # result2,diagnostics2 = evaluator.evaluate_with_diagnostics(cond, env2)
    # print(f"User2 result: {result2}")
    # if not result2:
    #     print_diagnostics(diagnostics2)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
