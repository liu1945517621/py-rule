from condition.condition import Condition, Op, ValType, JoinOp
from runtime.executor import Executor
from runtime.loader import Loader
import asyncio


class Actor:
    def __init__(self, name: str):
        self.Name = name
        self.age = 0
        self.tags = []

    def Age(self) -> int:
        return self.age

    def SetAge(self, age: int):
        self.age = age

    def Tags(self) -> list:
        return self.tags

    def SetTags(self, tags: list):
        self.tags = tags


class BaseLoader(Loader):
    def __init__(self):
        super().__init__("BaseLoader", 5)

    async def load(self, condition: Condition, items: list) -> list:
        name_to_age = {
            "Peppa": 5,
            "George": 3,
            "Suzy Sheep": 6,
            "Richard Rabbit": 30,
            "Candy Cat": 7,
            "Danny Dog": 8,
            "Amo Duck": 4,
            "Bull Bear": 35,
            "Mommy Pig": 38,
            "Daddy Pig": 40,
        }

        for item in items:
            if isinstance(item, Actor):
                item.SetAge(name_to_age.get(item.Name, 0))

        return []  # 所有项都成功加载


class TagsLoader(Loader):
    def __init__(self):
        super().__init__("TagsLoader", 10)

    async def load(self, condition: Condition, items: list) -> list:
        name_to_tags = {
            "Peppa": ["Pig", "Minor"],
            "George": ["Pig", "Minor"],
            "Suzy Sheep": ["Sheep", "Minor"],
            "Richard Rabbit": ["Rabbit", "Adult"],
            "Candy Cat": ["Cat", "Minor"],
            "Danny Dog": ["Dog", "Minor"],
            "Amo Duck": ["Duck", "Minor"],
            "Bull Bear": ["Bear", "Adult"],
            "Mommy Pig": ["Pig", "Adult"],
            "Daddy Pig": ["Pig", "Adult"],
        }

        for item in items:
            if isinstance(item, Actor):
                item.SetTags(name_to_tags.get(item.Name, []))

        return []  # 所有项都成功加载


async def main():
    # 构造条件
    cond = Condition()
    cond.join_op = JoinOp.AND
    cond.conditions = [
        Condition("Age()", Op.GT, "4", ValType.INT),
        Condition("Tags()", Op.CONTAINS_ANY, '["Pig"]', ValType.STRING)
    ]

    # 创建加载器
    loaders = [BaseLoader(), TagsLoader()]

    # 创建执行器
    executor = Executor(cond, loaders, Actor)

    # 创建测试数据
    items = [
        Actor("Peppa"),
        Actor("George"),
        Actor("Suzy Sheep"),
        Actor("Richard Rabbit"),
        Actor("Mommy Pig"),
        Actor("Daddy Pig"),
    ]

    # 执行
    result = await executor.execute(items)

    # 输出结果
    print(f"{'Name':<15}{'Result':<12}")
    print("-" * 27)

    for item in result.matched_items:
        actor = item.item
        print(f"{actor.Name:<15}{'符合':<12}")

    for item in result.not_matched_items:
        actor = item.item
        reason = item.reason or ""
        print(f"{actor.Name:<15}{'不符':<12}")


if __name__ == "__main__":
    asyncio.run(main())
