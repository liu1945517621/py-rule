1. condition.py
核心作用：定义 Condition 类，作为条件表达式的基础数据结构，支持条件的创建、克隆、比较、逻辑运算（取反、简化）等。
主要功能：
表示单字段条件（如 field=age, op=EQ, val=18）和组合条件（如 join_op=AND, conditions=[cond1, cond2]）。
提供条件判断方法（is_empty/is_join/is_always_true 等）。
支持逻辑运算（not_ 取反、simplify 简化表达式）。
工具函数（And/Or/Not）用于快速创建组合条件。

2. op.py
核心作用：定义条件运算相关的枚举类型，规范比较操作符和逻辑连接符。
主要功能：
Op 枚举：定义比较操作符（如 EQ 等于、GT 大于、IN 包含于等），并提供操作符文本描述和正向转换（如 NE 转换为 NOT EQ）。
JoinOp 枚举：定义逻辑连接符（AND/OR/NOT），用于组合条件间的逻辑关系。

3. var.py
核心作用：定义值类型枚举及值类型相关工具类，规范条件中值的类型。
主要功能：
ValType 枚举：定义支持的值类型（如 INT/STRING/TIME/GROUP 等）。
ValAndType 类：组合值和类型，提供类型代码和文本描述。 

4. func.py
核心作用：提供条件表达式中常用的函数实现（如时间处理、包含判断等）。
主要功能：
时间相关：add_period_func（时间加减）、today_func（获取当前日期）。
包含判断：contains_any_func（关键词 / 非关键词模式的包含检查）。
零值判断：is_not_zero_func（判断值是否非空 / 非零）。

5. utils.py
核心作用：提供通用工具函数，辅助数据类型判断。
主要功能：
is_collection：判断对象是否为集合类型（列表、元组等，排除字符串）。
is_empty：判断对象是否为空（None、空集合等）。

6. convert.py
核心作用：提供条件表达式的转换功能，支持字段映射和值映射。
主要功能：
ConvertMapping：定义字段和值的映射关系（如源字段 age 映射到目标字段 user_age）。
convert_condition：递归转换条件中的字段和值，支持多转换器组合（join_converters）。

7. meta.py
核心作用：定义条件元数据，描述字段支持的操作符、值类型等信息。
主要功能：
Meta 类：存储字段元信息（支持的操作符、值类型、可选值等）。
MetaValue 类：描述元数据中的可选值（值、类型、名称等）。
工具函数：从外部数据源（如分组提供者）生成 MetaValue 列表

8. selector.py
核心作用：定义选择器接口，用于筛选条件中的特定字段或条件。
主要功能：
Selector 接口：提供 match 方法判断条件是否符合筛选规则。
DefaultSelector：支持按包含字段、排除字段、自定义谓词筛选条件。
工具函数：join_selector（组合多个选择器）、not_selector（取反选择器）。

9. values.py
核心作用：提供值处理工具函数，支持字符串去引号、值类型转换等。
主要功能：
unquote：去除字符串首尾引号。
val_to_int64_slice/val_to_string_slice：将字符串转换为整数 / 字符串列表（支持 JSON 数组和逗号分隔格式）。

10. in_group.py
核心作用：定义群组匹配接口，用于判断值是否属于某个群组。
主要功能：
InGrouper 接口：提供 in_groups 方法判断值是否在指定群组中，支持自定义群组匹配逻辑（如 Redis 群组）。

11. context.py
核心作用：定义上下文类，用于存储和获取键值对数据，支持线程安全操作。
主要功能：
线程安全的键值对存储（set/get 方法）。
类型化获取值（get_string/get_bool/get_int64）。