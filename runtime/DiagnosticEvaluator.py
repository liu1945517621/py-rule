from condition import Condition, JoinOp
from expr.value_handle.factory import HandlerFactory
from expr.expr import expr


class DiagnosticEvaluator:
    def __init__(self, functions):
        self.functions = functions
        self.handler_factory = HandlerFactory()

    def evaluate_with_diagnostics(self, cond: Condition, env: dict):
        """带诊断信息的评估"""
        if cond.join_op != JoinOp.AND:
            # 简单处理非AND条件
            expr_str = expr(cond)
            try:
                result = eval(expr_str, {"__builtins__": {}, **self.functions}, env)
                return result, []
            except Exception as e:
                return False, [f"评估出错: {e}"]

        # 分别评估每个条件
        diagnostics = []
        all_passed = True

        for sub_cond in cond.conditions:
            # 创建单独条件进行评估
            single_cond = Condition()
            single_cond.field = sub_cond.field
            single_cond.op = sub_cond.op
            single_cond.val = sub_cond.val
            single_cond.val_type = sub_cond.val_type

            expr_str = expr(single_cond)
            try:
                result = eval(expr_str, {"__builtins__": {}, **self.functions}, env)

                # 获取字段实际值
                field_key = sub_cond.field.rstrip("()")
                actual_value = env.get(field_key)

                # 生成建议
                suggestions = []
                if not result:
                    suggestions = self.handler_factory.get_suggestions(sub_cond, actual_value)

                diagnostics.append({
                    "condition": sub_cond,
                    "passed": result,
                    "actual_value": actual_value,
                    "suggestions": suggestions
                })

                if not result:
                    all_passed = False

            except Exception as e:
                diagnostics.append({
                    "condition": sub_cond,
                    "passed": False,
                    "error": str(e),
                    "suggestions": [f"条件评估出错: {e}"]
                })
                all_passed = False

        return all_passed, diagnostics


def print_diagnostics(diagnostics):
    """打印诊断结果"""
    print("条件评估详情:")
    for diag in diagnostics:
        cond = diag["condition"]
        if "error" in diag:
            print(f"  ❌ {cond.field} {cond.op.code()} {cond.val}")
            print(f"     错误: {diag['error']}")
        else:
            status = "✅" if diag["passed"] else "❌"
            print(f"  {status} {cond.field} {cond.op.code()} {cond.val}")
            if not diag["passed"]:
                print(f"     实际值: {diag['actual_value']}")
                for suggestion in diag["suggestions"]:
                    print(f"     建议: {suggestion}")
