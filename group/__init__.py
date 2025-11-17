from .group import Status,DataSourceType,DataType,DataSource,Group

# 导出所有公共类和枚举
__all__ = [
    'Status',
    'DataSourceType',
    'DataType',
    'DataSource',
    'Group'
]

#  ((Id==1)and(Name()=="A Mao")and(ContainsAny(month, [3,7,11], false)))
#  (((Id==1)or(Name()=="A Mao"))and(ContainsAny(month, [3,7,11], false)))
#  (((Name()=="A Mao"))and(ContainsAny(month, [3,7,11], false)))
#  (((Id==1))and(ContainsAny(month, [3,7,11], false)))