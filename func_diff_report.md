## condition/func.go vs condition/func.py 差异报告

### 1. 功能覆盖面
- Go 版提供 AddPeriod、Today、InGroups 全家桶（含构建器/Provider 刷新/并发执行）、InBICrowd（Redis 交互）、ContainsAny、IsNotZero 等完整函数集；Go 还依赖 `period`, `group`, `redis`, `funk` 等模块。
- Python 版目前仅实现 AddPeriod、Today、ContainsAny、IsNotZero 及其内部辅助函数，完全缺失 InGroups、InBICrowd 及相关 Provider/Redis 逻辑，也没有通用零值判断工具（依赖手写类型分支）。
- 结论：Python 只能构建表达式，无法执行群组、人群包等高级函数，若要与 Go 保持一致，需要新增大量业务方法。

### 2. AddPeriod 差异
- Go：通过 `period.Unit` 枚举解析 unit，并调用 `unit.Add(now, duration)`，自动处理所有单位、返回错误信息明确。
```0:48:f:\goProject\go-rule\condition\func.go
unit := period.Unit(unitInt)
afterTime = unit.Add(now, duration)
```
- Python：手动判断 `unit_int` 是否为 2/3/4/5，直接对 datetime 字段 `replace`，未实现 date 类型，也没封装错误。
```16:38:condition/func.py
if unit_int == 2:
    return now.replace(second=now.second + duration)
```
- 建议：引入 period 枚举或常量，统一单位校验和报错逻辑，支持更多时间单位。

### 3. ContainsAny 实现差异
- Go：根据 `keyword` 切换两套实现，严格校验参数类型（字符串/列表/整型），可返回详细错误。
```369:385:f:\goProject\go-rule\condition\func.go
if keyword {
    return containsAnyForKeyword(params...)
} else {
    return containsAnyForNotKeyword(params...)
}
```
- Python：简化处理，仅判断 iterable，对非字符串/列表的类型无明确处理，也无错误提示。
```54:92:condition/func.py
if keyword:
    return _contains_any_for_keyword(params)
else:
    return _contains_any_for_not_keyword(params)
``>
- 建议：复刻 Go 的类型校验与错误信息，确保行为一致。

### 4. IsNotZero 差异
- Go：利用 `funk.IsZero` + `funk.IsEmpty`，支持任意类型且逻辑集中。
```448:462:f:\goProject\go-rule\condition\func.go
func IsNotZero(v interface{}) bool {
    return !funk.IsZero(v) && !funk.IsEmpty(v)
}
```
- Python：手写类型判断，仅覆盖数字/字符串/序列/字典，缺少对布尔、集合等类型的处理，语义也与 Go 有差距。
```95:118:condition/func.py
if isinstance(param, (int, float)):
    return param != 0
```
- 建议：扩展零值判断逻辑，或引入第三方工具以覆盖更多类型。

### 5. 缺失的业务函数
- InGroups：Go 版包含 `InGroupsFuncBuilder`、Provider 同步、Ticker 刷新、并发调用，本质是群组匹配引擎。
```65:258:f:\goProject\go-rule\condition\func.go
type InGroupsFuncBuilder interface { ... }
```
- InBICrowd：Go 版通过 Redis Bitmap 查人群包，并做缓存；Python 缺乏任何等效实现。
```260:361:f:\goProject\go-rule\condition\func.go
func InBICrowdFunc(keyPrefix string, redisPool redis.Pool) ...
```
- 建议：根据业务需求在 Python 端补齐接口（可以先提供占位实现），否则 ValueHandler 中的 `InGroups` / `InBICrowd` 表达式无法落地执行。

### 6. 总结
- Python 版本目前只覆盖最基础的函数，无法完全复刻 Go 的运行时能力。
- 若目标是跨语言一致，需要：
  1. 引入 period 单位枚举及校验；
  2. 扩展 ContainsAny 和 IsNotZero 的类型处理；
  3. 实现 InGroups / InBICrowd / IsNotZero 等缺失函数；
  4. 与 Go 版保持错误信息与行为一致。

