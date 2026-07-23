from __future__ import annotations

from enum import Enum


class ValueType(Enum):
    """值类型。"""

    NONE = 0
    STRING = 1
    INTEGER = 2
    FLOAT = 3
    BOOLEAN = 4
    STRING_LIST = 5
    INTEGER_LIST = 6
    FLOAT_LIST = 7
    BOOLEAN_LIST = 8


def is_zero(value: Value) -> bool:
    """按类型判定是否为"零"。

    - NONE: 始终为 True
    - INTEGER / FLOAT: 值等于 0
    - BOOLEAN: 值为 False
    - STRING / 列表类型: 长度为 0
    """
    if value.type == ValueType.NONE:
        return True
    elif value.type in (ValueType.INTEGER, ValueType.FLOAT):
        return value.raw == 0
    elif value.type == ValueType.BOOLEAN:
        return not value.raw
    elif value.type in (
        ValueType.STRING,
        ValueType.STRING_LIST,
        ValueType.INTEGER_LIST,
        ValueType.FLOAT_LIST,
        ValueType.BOOLEAN_LIST,
    ):
        return len(value.raw) == 0
    return False


def is_positive(value: Value) -> bool:
    """按类型判定是否为"正"。是 is_zero 的取反。"""
    return not is_zero(value)


def clamp_if_negative(value: Value):
    """若为非负整数/浮点且值为负，截断为 0。"""
    if value.type == ValueType.INTEGER and value.raw < 0:
        value._raw = 0
    elif value.type == ValueType.FLOAT and value.raw < 0.0:
        value._raw = 0.0


class Value:
    """封装值及其类型。"""

    def __init__(self, value_type: ValueType, raw_value):
        self._type = value_type
        self._raw = raw_value
        self._validate()

    def _validate(self):
        """校验 raw_value 的类型是否匹配 value_type。"""
        if self._type == ValueType.NONE:
            if self._raw is not None:
                raise TypeError(
                    f"类型不匹配：期望 None，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.STRING:
            if not isinstance(self._raw, str):
                raise TypeError(
                    f"类型不匹配：期望 str，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.INTEGER:
            if not isinstance(self._raw, int) or isinstance(self._raw, bool):
                raise TypeError(
                    f"类型不匹配：期望 int，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.FLOAT:
            if not isinstance(self._raw, float):
                raise TypeError(
                    f"类型不匹配：期望 float，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.BOOLEAN:
            if not isinstance(self._raw, bool):
                raise TypeError(
                    f"类型不匹配：期望 bool，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.STRING_LIST:
            if not isinstance(self._raw, list) or not all(isinstance(v, str) for v in self._raw):
                raise TypeError(
                    f"类型不匹配：期望 list[str]，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.INTEGER_LIST:
            if not isinstance(self._raw, list) or not all(
                isinstance(v, int) and not isinstance(v, bool) for v in self._raw
            ):
                raise TypeError(
                    f"类型不匹配：期望 list[int]，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.FLOAT_LIST:
            if not isinstance(self._raw, list) or not all(isinstance(v, float) for v in self._raw):
                raise TypeError(
                    f"类型不匹配：期望 list[float]，实际为 {type(self._raw).__name__}"
                )
        elif self._type == ValueType.BOOLEAN_LIST:
            if not isinstance(self._raw, list) or not all(isinstance(v, bool) for v in self._raw):
                raise TypeError(
                    f"类型不匹配：期望 list[bool]，实际为 {type(self._raw).__name__}"
                )

    @property
    def type(self) -> ValueType:
        """值的类型。"""
        return self._type

    @property
    def raw(self):
        """返回原始 Python 值。"""
        return self._raw
