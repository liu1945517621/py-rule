import redis
from typing import List, Tuple, Callable, Any, Optional, Dict
from datetime import datetime

import group
from .context import Context
from abc import ABC, abstractmethod


class InGrouper:
    """自定义实现InGroups实现"""

    def match(self, ctx: Context, field_val_str: str, params: List[Any]) -> bool:
        """是否由该实现处理"""
        raise NotImplementedError

    def key(self, ctx: Context, field_val_str: str, params: List[Any]) -> Tuple[str, Exception]:
        """生成Key"""
        raise NotImplementedError

    def in_groups(self, ctx: Context, field_val_str: str, params_list: List[List[Any]]) -> Tuple[bool, Exception]:
        """是否在群组中"""
        raise NotImplementedError


class InRedisGroup(InGrouper):
    """通过 redis key的ttl实现InGroups"""

    def __init__(self, redis_pool: redis.Redis, match_keys: List[str] = None):
        self.redis_pool = redis_pool
        self.match_keys = match_keys or []

    def match(self, ctx: Context, field_val_str: str, params: List[Any]) -> bool:
        if len(self.match_keys) == 0:
            return True
        if len(params) > 0 and isinstance(params[0], str):
            return params[0] in self.match_keys
        return False

    def key(self, ctx: Context, field_val_str: str, params: List[Any]) -> tuple[str, ValueError] | tuple[
        Any, None] | tuple[str, Exception]:
        if len(params) == 0:
            return "", ValueError("InRedisGroup params must not be empty")
        if not isinstance(params[0], str):
            return "", ValueError(f"InRedisGroup first param {params[0]} is not a string")
        try:
            key = params[0] % field_val_str
            return key, None
        except Exception as e:
            return "", e

    def in_groups(self, ctx: Context, field_val_str: str, params_list: List[List[Any]]) -> tuple[
                                                                                               bool, None] | \
                                                                                           tuple[
                                                                                               bool, Exception] | \
                                                                                           tuple[
                                                                                               bool, Any] | \
                                                                                           tuple[
                                                                                               bool, ValueError]:
        """判断是否在群组中

        Args:
            ctx: 上下文变量
            field_val_str: 字段实际值，如用户ID
            params_list: 参数列表，每个参数包含:
                - params[0] group    群组名,redis key format
                - params[1] initTTL  redis key过期时间，可选
                - params[2] afterAt  是否在某个时间点之后，可选
                - params[3] beforeAt 是否在某个时间点之前，可选
        """
        if len(params_list) == 0:
            return True, None

        result = False
        now = datetime.now()
        to_be_load_inputs = []

        # 先从本次请求Context尝试获取，防止同一个逻辑多次执行，都要走到IO
        for params in params_list:
            key, inner_err = self.key(ctx, field_val_str, params)
            if inner_err:
                return False, inner_err

            storage = ctx.get_int(key)
            if key in storage:
                remaining_ttl = storage[key]
                inner_result, inner_err = self._in_group(now, remaining_ttl, params)
                if inner_err:
                    return False, inner_err
                if inner_result:
                    return True, None
            else:
                to_be_load_inputs.append(params)

        if len(to_be_load_inputs) == 0:
            return result, None

        try:
            # 使用pipeline优化多个key的TTL查询
            if len(to_be_load_inputs) == 1:
                params = to_be_load_inputs[0]
                key, _ = self.key(ctx, field_val_str, params)
                remaining_ttl = self.redis_pool.ttl(key)

                # 存储到上下文变量
                ctx.set(key, remaining_ttl)

                return self._in_group(now, remaining_ttl, params)
            else:
                # 批量获取多个key的TTL
                keys = []
                for params in to_be_load_inputs:
                    key, _ = self.key(ctx, field_val_str, params)
                    keys.append(key)

                # 使用mget或者pipeline方式获取TTL（这里简化处理）
                pipeline_results = []
                for key in keys:
                    ttl = self.redis_pool.ttl(key)
                    pipeline_results.append(ttl)

                # 处理pipeline结果
                for i, params in enumerate(to_be_load_inputs):
                    remaining_ttl = pipeline_results[i]
                    if not isinstance(remaining_ttl, int):
                        continue

                    key, _ = self.key(ctx, field_val_str, params)
                    # 存储到上下文变量
                    ctx.set(key, remaining_ttl)

                    inner_result, inner_err = self._in_group(now, remaining_ttl, params)
                    if inner_err:
                        return False, inner_err
                    if inner_result:
                        result = True

                return result, None

        except Exception as e:
            return False, e

    def _in_group(self, now: datetime, remaining_ttl: int, params: List[Any]) -> tuple[bool, None] | tuple[
        bool, ValueError]:
        """判断是否在群组中"""
        result = False

        # 有存在，但未设置过期时间，则认为它是有在群组中
        if remaining_ttl == -1:
            return True, None

        if remaining_ttl <= 0:
            return False, None

        # 如果参数小于等于，则说明没有afterAt参数，不需要判断afterAt
        if len(params) <= 2:
            return True, None

        try:
            init_ttl = int(params[1])
        except (ValueError, TypeError):
            return False, ValueError(f"InGroups param[1] must be int")

        if len(params) > 2:
            after_at = params[2]
            if not isinstance(after_at, datetime):
                return False, ValueError("InGroups param[2] must be datetime")

            occur_unix = int(now.timestamp()) + remaining_ttl - init_ttl

            if len(params) > 3:
                before_at = params[3]
                if isinstance(before_at, datetime) and before_at.timestamp() < occur_unix:
                    return False, None

            if occur_unix >= after_at.timestamp():
                result = True

        return result, None


# 定义GroupToInGrouperConverter接口
class GroupToInGrouperConverter(ABC):
    """群组与InGrouper的转换器"""

    @abstractmethod
    def match(self, g: group.Group) -> bool:
        """该群组是否由该转换器转换"""
        pass

    @abstractmethod
    def in_grouper_index(self, g: group.Group) -> str:
        """InGrouper的分组标识，如同是InRedisGrouper，会根据Redis的配置再分组"""
        pass

    @abstractmethod
    def convert(self, groups: List[group.Group]) -> Tuple[InGrouper, Exception]:
        """转换"""
        pass


# 全局变量
AllGroupToInGrouperConverters: List[GroupToInGrouperConverter] = []


class GroupToInRedisGroupConverter(GroupToInGrouperConverter):
    """Redis群组转换器"""

    def match(self, g: group.Group) -> bool:
        """判断群组是否为Redis类型"""
        return g.data_source.type == group.DataSourceType.REDIS

    def in_grouper_index(self, g: group.Group) -> str:
        """生成Redis群组的分组标识"""
        data_source = g.data_source
        return f"{data_source.type}:{data_source.addrs}:{data_source.user}:{data_source.db}"

    def convert(self, groups: List[group.Group]) -> tuple[None, ValueError] | tuple[None, RuntimeError] | tuple[
        None, Any] | tuple[InRedisGroup, None] | tuple[None, Exception]:
        """将群组转换为InRedisGroup"""
        try:
            keys = []
            for g in groups:
                keys.append(g.data_source.key_format)

            conf = groups[0].data_source
            try:
                db = int(conf.db)
            except (ValueError, TypeError) as e:
                return None, ValueError(f"Invalid DB value: {e}")

            # 使用python的方法创建Redis连接池
            redis_pool = redis.ConnectionPool(
                host=conf.addrs[0],
                port=conf.addrs[1],
                password=conf.password,
                db=db,
                pool_size=16
            )
            client = redis.Redis(connection_pool=redis_pool)

            in_grouper = InRedisGroup(client, keys)
            return in_grouper, None

        except Exception as e:
            return None, e


# 初始化全局转换器列表
AllGroupToInGrouperConverters.append(GroupToInRedisGroupConverter())
