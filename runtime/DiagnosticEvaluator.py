from condition import Condition, JoinOp
from expr.value_handle.factory import HandlerFactory
from expr.expr import expr

class DiagnosticEvaluator:
    def __init__(self, functions):
        self.functions = functions
        self.handler_factory = HandlerFactory()

    def evaluate_with_diagnostics(self, cond: Condition, env: dict):
        """带诊断信息的评估"""
        # 如果是连接条件（AND）
        if cond.join_op == JoinOp.AND:
            diagnostics = []
            all_passed = True

            for sub_cond in cond.conditions:
                result, sub_diagnostics = self.evaluate_with_diagnostics(sub_cond, env)
                diagnostics.extend(sub_diagnostics)

                if not result:
                    all_passed = False

            return all_passed, diagnostics

        # 如果是其他连接条件（OR/NOT等）
        elif cond.is_join():
            return self._evaluate_non_and_condition(cond, env)

        # 如果是叶子条件（基础条件）
        else:
            # 这里应该添加原来的叶子条件评估逻辑
            expr_str = expr(cond)
            try:
                result = eval(expr_str, {"__builtins__": {}, **self.functions}, env)

                # 获取字段实际值
                if cond.field:
                    if cond.field.endswith("()"):
                        # 提取不带括号的方法名，并尝试调用该方法
                        method_name = cond.field[:-2]
                        if method_name in env and callable(env[method_name]):
                            try:
                                actual_value = env[method_name]()
                            except Exception as e:
                                actual_value = f"Error calling {method_name}: {str(e)}"
                        else:
                            actual_value = f"Method '{method_name}' not found or not callable"
                    else:
                        # 直接从环境变量中获取字段值
                        actual_value = env.get(cond.field)
                else:
                    actual_value = None


                # 生成建议
                suggestions = []
                if not result:
                    suggestions = self.handler_factory.get_suggestions(cond, actual_value)

                diagnostic = {
                    "condition": cond,
                    "passed": result,
                    "actual_value": actual_value,
                    "suggestions": suggestions
                }

                return result, [diagnostic]

            except Exception as e:
                diagnostic = {
                    "condition": cond,
                    "passed": False,
                    "error": str(e),
                    "suggestions": [f"条件评估出错: {e}"]
                }
                return False, [diagnostic]


    def _evaluate_non_and_condition(self, cond: Condition, env: dict):
        """评估非AND条件"""
        if cond.join_op == JoinOp.OR:
            # 递归评估OR条件中的每个子条件
            diagnostics = []
            any_passed = False

            for sub_cond in cond.conditions:
                result, sub_diagnostics = self.evaluate_with_diagnostics(sub_cond, env)
                diagnostics.extend(sub_diagnostics)
                if result:
                    any_passed = True

            return any_passed, diagnostics

        elif cond.join_op == JoinOp.NOT:
            # 评估NOT条件中的子条件并反转结果
            if len(cond.conditions) == 1:
                result, diagnostics = self.evaluate_with_diagnostics(cond.conditions[0], env)
                return not result, diagnostics
            else:
                # 简单处理NOT条件（保持原有逻辑）
                expr_str = expr(cond)
                try:
                    result = eval(expr_str, {"__builtins__": {}, **self.functions}, env)
                    return result, []
                except Exception as e:
                    return False, [f"评估出错: {e}"]

        else:
            # 其他非AND条件保持原有逻辑
            expr_str = expr(cond)
            try:
                result = eval(expr_str, {"__builtins__": {}, **self.functions}, env)
                return result, []
            except Exception as e:
                return False, [f"评估出错: {e}"]

def print_diagnostics(diagnostics):
    """打印诊断结果"""
    print("条件评估详情:")
    for diag in diagnostics:
        cond = diag["condition"]
        if "error" in diag:
            # 安全地处理可能为None的属性
            field_str = getattr(cond, 'field', '') or ''
            op_str = getattr(cond, 'op', None)
            op_code = op_str.code() if op_str else ''
            val_str = getattr(cond, 'val', '') or ''
            print(f"  ❌ {field_str} {op_code} {val_str}")
            print(f"     错误: {diag['error']}")
        else:
            status = "✅" if diag["passed"] else "❌"
            # 安全地处理可能为None的属性
            field_str = getattr(cond, 'field', '') or ''
            op_str = getattr(cond, 'op', None)
            op_code = op_str.code() if op_str else ''
            val_str = getattr(cond, 'val', '') or ''
            print(f"  {status} {field_str} {op_code} {val_str}")
            if not diag["passed"]:
                print(f"     实际值: {diag['actual_value']}")
                for suggestion in diag["suggestions"]:
                    print(f"     建议: {suggestion}")
