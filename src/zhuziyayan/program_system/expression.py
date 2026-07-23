from __future__ import annotations

from abc import ABC, abstractmethod

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.value import Value, ValueType


# 列表类型到元素类型的映射
_LIST_TO_ELEMENT_TYPE = {
    ValueType.STRING_LIST: ValueType.STRING,
    ValueType.INTEGER_LIST: ValueType.INTEGER,
    ValueType.FLOAT_LIST: ValueType.FLOAT,
    ValueType.BOOLEAN_LIST: ValueType.BOOLEAN,
}


def list_element_type(list_type: ValueType) -> ValueType | None:
    """给定列表类型，返回其元素类型。非列表类型返回 None。"""
    return _LIST_TO_ELEMENT_TYPE.get(list_type)


class ValueExpression(ABC):
    """值返回表达式：无副作用的、可求值的表达式。

    所有 evaluate() 不抛异常——遇到特殊情况返回 Value(ValueType.NONE, None)。
    """

    @abstractmethod
    def evaluate(self, context: Context) -> Value:
        """在给定上下文中求值，返回 Value 对象。"""
        ...


class VariableExpression(ValueExpression):
    """变量表达式。引用一个已定义的变量，求值即返回该变量的值。"""

    def __init__(self, variable_name: str):
        self._variable_name = variable_name

    @property
    def variable_name(self) -> str:
        """被引用的变量名。"""
        return self._variable_name

    def evaluate(self, context: Context) -> Value:
        if not context.has_variable(self._variable_name):
            return Value(ValueType.NONE, None)
        return context.get_variable(self._variable_name).value


class ListIndexExpression(ValueExpression):
    """列表索引表达式。访问列表指定位置（1-based）的元素。"""

    def __init__(self, variable_name: str, index: int):
        self._variable_name = variable_name
        self._index = index  # 1-based，按源码中的写法存储

    @property
    def variable_name(self) -> str:
        """列表变量名。"""
        return self._variable_name

    @property
    def index(self) -> int:
        """索引（1-based）。"""
        return self._index

    def evaluate(self, context: Context) -> Value:
        if not context.has_variable(self._variable_name):
            return Value(ValueType.NONE, None)
        var = context.get_variable(self._variable_name)
        list_value = var.value.raw
        zero_based = self._index - 1
        if zero_based < 0 or zero_based >= len(list_value):
            return Value(ValueType.NONE, None)
        element = list_value[zero_based]
        element_type = list_element_type(var.value.type) or ValueType.NONE
        return Value(element_type, element)
