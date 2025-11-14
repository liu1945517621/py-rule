from typing import List, Any
from condition.condition import Condition
import asyncio


class Loader:
    def __init__(self, name: str, cost: int = 0):
        self.name = name
        self.cost = cost

    async def load(self, condition: Condition, items: List[Any]) -> List[Any]:
        """
        加载数据
        返回未加载的项列表
        """
        return []
