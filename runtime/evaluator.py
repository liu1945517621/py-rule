from typing import Callable, Any
from condition.condition import Condition


class Evaluator:
    def __init__(self, condition: Condition, evaluate_func: Callable):
        self.condition = condition
        self.evaluate_func = evaluate_func

    def evaluate(self, env: Any) -> bool:
        return self.evaluate_func(env)
