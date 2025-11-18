from enum import IntEnum
from typing import List

class ValType(IntEnum):
    """值类型枚举"""
    INT = 1        # 整型
    STRING = 2     # 字符串
    BOOL = 3       # 布尔
    FLOAT = 4      # 浮点
    TIME = 8       # 时间
    TIME_BEFORE = 9   # 现在之前
    TIME_AFTER = 10   # 现在之后
    BI_CROWD = 11     # BI人群包
    GROUP = 12        # 群组，可以使用ContainsAny及In操作，值由InGrouper处理
    VAR = 13          # 变量，可以引用到本表达式环境字段

# 所有值类型列表
AllValTypes: List[ValType] = [
    ValType.INT,
    ValType.STRING,
    ValType.BOOL,
    ValType.FLOAT,
    ValType.TIME,
    ValType.TIME_BEFORE,
    ValType.TIME_AFTER,
    ValType.GROUP,
    ValType.VAR,
    ValType.BI_CROWD,
]

class ValAndType:
    """值和类型组合"""
    def __init__(self, val: str = "", type_: ValType = None):
        self.val = val
        self.type = type_

    def code(self) -> int:
        """获取类型代码"""
        return int(self.type) if self.type else 0

    def text(self) -> str:
        """获取类型文本描述"""
        if not self.type:
            return "未知"

        type_map = {
            ValType.INT: "整型",
            ValType.STRING: "字符串",
            ValType.BOOL: "布尔",
            ValType.FLOAT: "浮点",
            ValType.TIME: "时间",
            ValType.TIME_BEFORE: "现在之前",
            ValType.TIME_AFTER: "现在之后",
            ValType.BI_CROWD: "BI人群包",
            ValType.GROUP: "群组",
            ValType.VAR: "变量",
        }

        return type_map.get(self.type, "未知")
