from __future__ import annotations

from zhuziyayan.program_system.value import Value, ValueType, clamp_if_negative


class Variable:
    """变量。

    持有一个名称和一个 Value 对象。
    非负整数/浮点类型变量强制不能为负——set_value 时自动截断。
    """

    def __init__(self, name: str, value: Value):
        self._name = name
        self._value = value
        self.set_value(value)

    @property
    def name(self) -> str:
        """变量的名称。"""
        return self._name

    @property
    def type(self) -> ValueType:
        """变量的类型（委托给 Value）。"""
        return self._value.type

    @property
    def value(self) -> Value:
        """变量的值（Value 对象）。"""
        return self._value

    def set_value(self, value: Value):
        """设置变量的值。

        自动对非负整数/浮点类型执行负数截断。
        设置时可能会改变变量类型。
        """
        clamp_if_negative(value)
        self._value = value
