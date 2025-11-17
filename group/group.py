from typing import List, Optional
from enum import IntEnum
from dataclasses import dataclass

class Status(IntEnum):
    """群组状态"""
    ENABLED = 1   # 生效中
    DISABLED = 2  # 已失效

class DataSourceType:
    """数据源类型"""
    REDIS = "Redis"

class DataType:
    """数据类型"""
    REDIS_STRING = "String"
    REDIS_BITMAP = "Bitmap"      # Bitmap
    REDIS_LIST = "List"
    REDIS_SET = "Set"
    REDIS_HASH = "Hash"
    REDIS_SORTED_SET = "SortedSet"

@dataclass
class DataSource:
    """数据源"""
    type: str = ""
    addrs: List[str] = None
    user: str = ""
    password: str = ""
    db: str = ""
    key_format: str = ""
    data_type: str = DataType.REDIS_STRING  # String Bitmap List Set Hash SortedSet，默认String
    
    def __post_init__(self):
        if self.addrs is None:
            self.addrs = []

@dataclass
class Group:
    """群组"""
    name: str = ""
    code: str = ""
    expiration_seconds: int = 0
    data_source: Optional[DataSource] = None
    status: Status = Status.DISABLED
    
    def __post_init__(self):
        if self.data_source is None:
            self.data_source = DataSource()
