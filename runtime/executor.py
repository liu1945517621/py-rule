from typing import List, Any, Dict, Optional, Callable
from condition.condition import Condition, JoinOp, Op
from .loader import Loader
from .evaluator import Evaluator
import asyncio


class ExecutedItem:
    def __init__(self, item: Any, reason: Optional[str] = None):
        self.item = item
        self.reason = reason


class ExecutedResult:
    def __init__(self):
        self.matched_items: List[ExecutedItem] = []
        self.not_matched_items: List[ExecutedItem] = []
        self.unloaded_items: List[ExecutedItem] = []


class Executor:
    def __init__(self, condition: Condition, loaders: List[Loader], env_type: type):
        self.condition = condition
        self.loaders = loaders
        self.env_type = env_type
        self.evaluator = self._create_evaluator()

    def _create_evaluator(self) -> Callable:
        from expr.expr import expr
        expr_str = expr(self.condition)
        return lambda env: eval(expr_str, {"__builtins__": {}}, self._get_env_vars(env))

    def _get_env_vars(self, env: Any) -> Dict:
        """获取环境变量"""
        vars_dict = {}
        if hasattr(env, '__dict__'):
            vars_dict.update(env.__dict__)
        # 添加方法调用支持
        for attr_name in dir(env):
            if callable(getattr(env, attr_name)) and not attr_name.startswith('_'):
                vars_dict[attr_name] = getattr(env, attr_name)()
        return vars_dict

    async def execute(self, items: List[Any]) -> ExecutedResult:
        result = ExecutedResult()

        if not self.loaders:
            # 无加载器直接评估
            for item in items:
                try:
                    matched = self.evaluator(item)
                    if matched:
                        result.matched_items.append(ExecutedItem(item))
                    else:
                        result.not_matched_items.append(ExecutedItem(item))
                except Exception as e:
                    result.not_matched_items.append(ExecutedItem(item, str(e)))
            return result

        filtered_items = items[:]

        # 按加载器顺序处理
        for loader in self.loaders:
            if filtered_items:
                # 加载数据
                unloaded_items = await loader.load(self.condition, filtered_items)

                # 处理未加载项
                unloaded_item_set = set(unloaded_items)
                result.unloaded_items.extend([ExecutedItem(item) for item in unloaded_items])

                # 过滤已加载项
                filtered_items = [item for item in filtered_items if item not in unloaded_item_set]

        # 最终评估
        for item in filtered_items:
            try:
                matched = self.evaluator(item)
                if matched:
                    result.matched_items.append(ExecutedItem(item))
                else:
                    result.not_matched_items.append(ExecutedItem(item))
            except Exception as e:
                result.not_matched_items.append(ExecutedItem(item, str(e)))

        return result
