"""测试 zhuziyayan.program_system.expression — ValueExpression 及其子类。"""

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.expression import (
    VariableExpression,
    ListIndexExpression,
    list_element_type,
)
from zhuziyayan.program_system.value import Value, ValueType


# =============================================================================
# list_element_type
# =============================================================================


class TestListElementType:
    """list_element_type 的单元测试。"""

    def test_字符串列表(self):
        assert list_element_type(ValueType.STRING_LIST) == ValueType.STRING

    def test_整数列表(self):
        assert list_element_type(ValueType.INTEGER_LIST) == ValueType.INTEGER

    def test_浮点数列表(self):
        assert list_element_type(ValueType.FLOAT_LIST) == ValueType.FLOAT

    def test_布尔值列表(self):
        assert list_element_type(ValueType.BOOLEAN_LIST) == ValueType.BOOLEAN

    def test_非列表类型返回None(self):
        assert list_element_type(ValueType.INTEGER) is None
        assert list_element_type(ValueType.NONE) is None


# =============================================================================
# VariableExpression
# =============================================================================


class TestVariableExpression:
    """VariableExpression 的单元测试。"""

    def test_求值已存在变量(self):
        ctx = Context(None)
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 42))
        expr = VariableExpression("甲子")
        result = expr.evaluate(ctx)
        assert result.type == ValueType.INTEGER
        assert result.raw == 42

    def test_求值不存在变量返回NONE(self):
        ctx = Context(None)
        expr = VariableExpression("不存在子")
        result = expr.evaluate(ctx)
        assert result.type == ValueType.NONE
        assert result.raw is None

    def test_变量名属性(self):
        expr = VariableExpression("甲子")
        assert expr.variable_name == "甲子"


# =============================================================================
# ListIndexExpression
# =============================================================================


class TestListIndexExpression:
    """ListIndexExpression 的单元测试。"""

    def test_正常索引访问(self):
        ctx = Context(None)
        ctx.set_variable("列子", Value(ValueType.STRING_LIST, ["甲", "乙", "丙"]))
        expr = ListIndexExpression("列子", 2)  # 1-based 索引 2
        result = expr.evaluate(ctx)
        assert result.type == ValueType.STRING
        assert result.raw == "乙"

    def test_索引1访问第一个元素(self):
        ctx = Context(None)
        ctx.set_variable("列子", Value(ValueType.INTEGER_LIST, [10, 20, 30]))
        expr = ListIndexExpression("列子", 1)
        result = expr.evaluate(ctx)
        assert result.raw == 10

    def test_列表不存在返回NONE(self):
        ctx = Context(None)
        expr = ListIndexExpression("不存在子", 1)
        result = expr.evaluate(ctx)
        assert result.type == ValueType.NONE

    def test_索引为零返回NONE(self):
        """0-based 为负时返回 NONE（1-based 索引须 ≥1）。"""
        ctx = Context(None)
        ctx.set_variable("列子", Value(ValueType.INTEGER_LIST, [1, 2]))
        expr = ListIndexExpression("列子", 0)
        result = expr.evaluate(ctx)
        assert result.type == ValueType.NONE

    def test_索引越界返回NONE(self):
        ctx = Context(None)
        ctx.set_variable("列子", Value(ValueType.INTEGER_LIST, [1, 2]))
        expr = ListIndexExpression("列子", 5)
        result = expr.evaluate(ctx)
        assert result.type == ValueType.NONE

    def test_空列表访问返回NONE(self):
        ctx = Context(None)
        ctx.set_variable("列子", Value(ValueType.STRING_LIST, []))
        expr = ListIndexExpression("列子", 1)
        result = expr.evaluate(ctx)
        assert result.type == ValueType.NONE

    def test_属性访问(self):
        expr = ListIndexExpression("列子", 3)
        assert expr.variable_name == "列子"
        assert expr.index == 3
