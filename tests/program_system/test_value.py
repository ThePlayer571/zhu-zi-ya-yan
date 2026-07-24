"""测试 zhuziyayan.program_system.value — Value、ValueType、辅助函数。"""

import pytest
from zhuziyayan.program_system.value import (
    Value,
    ValueType,
    is_zero,
    is_positive,
    clamp_if_negative,
)


# =============================================================================
# Value — 构造与验证
# =============================================================================


class TestValueConstruction:
    """Value 构造和类型验证的测试。"""

    def test_none值(self):
        v = Value(ValueType.NONE, None)
        assert v.type == ValueType.NONE
        assert v.raw is None

    def test_none值_非法raw抛出TypeError(self):
        with pytest.raises(TypeError):
            Value(ValueType.NONE, "not none")

    def test_字符串值(self):
        v = Value(ValueType.STRING, "hello")
        assert v.type == ValueType.STRING
        assert v.raw == "hello"

    def test_字符串值_非法raw(self):
        with pytest.raises(TypeError):
            Value(ValueType.STRING, 123)

    def test_整数值(self):
        v = Value(ValueType.INTEGER, 42)
        assert v.type == ValueType.INTEGER
        assert v.raw == 42

    def test_整数值_bool被拒绝(self):
        """Python bool 是 int 的子类，但应当被拒绝。"""
        with pytest.raises(TypeError):
            Value(ValueType.INTEGER, True)

    def test_浮点数值(self):
        v = Value(ValueType.FLOAT, 3.14)
        assert v.type == ValueType.FLOAT
        assert v.raw == 3.14

    def test_浮点数值_非法raw(self):
        with pytest.raises(TypeError):
            Value(ValueType.FLOAT, 5)

    def test_布尔值(self):
        v = Value(ValueType.BOOLEAN, True)
        assert v.type == ValueType.BOOLEAN
        assert v.raw is True

    def test_布尔值_非法raw(self):
        with pytest.raises(TypeError):
            Value(ValueType.BOOLEAN, 1)

    def test_字符串列表(self):
        v = Value(ValueType.STRING_LIST, ["a", "b"])
        assert v.type == ValueType.STRING_LIST
        assert v.raw == ["a", "b"]

    def test_字符串列表_空列表(self):
        v = Value(ValueType.STRING_LIST, [])
        assert v.raw == []

    def test_字符串列表_元素类型错误(self):
        with pytest.raises(TypeError):
            Value(ValueType.STRING_LIST, [1, 2])

    def test_整数列表(self):
        v = Value(ValueType.INTEGER_LIST, [1, 2, 3])
        assert v.type == ValueType.INTEGER_LIST
        assert v.raw == [1, 2, 3]

    def test_整数列表_bool元素被拒绝(self):
        with pytest.raises(TypeError):
            Value(ValueType.INTEGER_LIST, [1, True])

    def test_浮点数列表(self):
        v = Value(ValueType.FLOAT_LIST, [1.0, 2.5])
        assert v.raw == [1.0, 2.5]

    def test_布尔值列表(self):
        v = Value(ValueType.BOOLEAN_LIST, [True, False])
        assert v.raw == [True, False]


# =============================================================================
# is_zero
# =============================================================================


class TestIsZero:
    """is_zero 的单元测试。"""

    def test_none是零(self):
        assert is_zero(Value(ValueType.NONE, None)) is True

    def test_整数零(self):
        assert is_zero(Value(ValueType.INTEGER, 0)) is True

    def test_整数非零(self):
        assert is_zero(Value(ValueType.INTEGER, 5)) is False

    def test_浮点数零(self):
        assert is_zero(Value(ValueType.FLOAT, 0.0)) is True

    def test_浮点数非零(self):
        assert is_zero(Value(ValueType.FLOAT, 3.14)) is False

    def test_布尔假是零(self):
        assert is_zero(Value(ValueType.BOOLEAN, False)) is True

    def test_布尔真非零(self):
        assert is_zero(Value(ValueType.BOOLEAN, True)) is False

    def test_空字符串是零(self):
        assert is_zero(Value(ValueType.STRING, "")) is True

    def test_非空字符串非零(self):
        assert is_zero(Value(ValueType.STRING, "hello")) is False

    def test_空列表是零(self):
        assert is_zero(Value(ValueType.STRING_LIST, [])) is True
        assert is_zero(Value(ValueType.INTEGER_LIST, [])) is True
        assert is_zero(Value(ValueType.FLOAT_LIST, [])) is True
        assert is_zero(Value(ValueType.BOOLEAN_LIST, [])) is True

    def test_非空列表非零(self):
        assert is_zero(Value(ValueType.INTEGER_LIST, [1])) is False


# =============================================================================
# is_positive
# =============================================================================


class TestIsPositive:
    """is_positive 的单元测试。"""

    def test_none非正(self):
        assert is_positive(Value(ValueType.NONE, None)) is False

    def test_零非正(self):
        assert is_positive(Value(ValueType.INTEGER, 0)) is False

    def test_非零为正(self):
        assert is_positive(Value(ValueType.INTEGER, 5)) is True

    def test_空字符串非正(self):
        assert is_positive(Value(ValueType.STRING, "")) is False

    def test_非空字符串为正(self):
        assert is_positive(Value(ValueType.STRING, "a")) is True


# =============================================================================
# clamp_if_negative
# =============================================================================


class TestClampIfNegative:
    """clamp_if_negative 的单元测试。"""

    def test_正整数不变(self):
        v = Value(ValueType.INTEGER, 5)
        clamp_if_negative(v)
        assert v.raw == 5

    def test_负整数截断为零(self):
        v = Value(ValueType.INTEGER, -5)
        clamp_if_negative(v)
        assert v.raw == 0

    def test_正浮点数不变(self):
        v = Value(ValueType.FLOAT, 3.14)
        clamp_if_negative(v)
        assert v.raw == 3.14

    def test_负浮点数截断为零(self):
        v = Value(ValueType.FLOAT, -2.5)
        clamp_if_negative(v)
        assert v.raw == 0.0

    def test_其他类型不受影响(self):
        v = Value(ValueType.STRING, "hello")
        clamp_if_negative(v)
        assert v.raw == "hello"


# =============================================================================
# to_literal_string
# =============================================================================


class TestToLiteralString:
    """Value.to_literal_string 的单元测试。"""

    def test_none(self):
        assert Value(ValueType.NONE, None).to_literal_string() == "无"

    def test_字符串(self):
        assert Value(ValueType.STRING, "hello").to_literal_string() == "hello"

    def test_整数(self):
        assert Value(ValueType.INTEGER, 123).to_literal_string() == "一百二十三"
        assert Value(ValueType.INTEGER, 0).to_literal_string() == "零"

    def test_浮点数(self):
        assert Value(ValueType.FLOAT, 3.14).to_literal_string() == "三又一秒四厘"

    def test_布尔真(self):
        assert Value(ValueType.BOOLEAN, True).to_literal_string() == "是"

    def test_布尔假(self):
        assert Value(ValueType.BOOLEAN, False).to_literal_string() == "否"

    def test_字符串列表(self):
        assert Value(ValueType.STRING_LIST, ["甲", "乙"]).to_literal_string() == "甲、乙"

    def test_整数列表(self):
        assert Value(ValueType.INTEGER_LIST, [1, 2]).to_literal_string() == "一、二"

    def test_浮点数列表(self):
        result = Value(ValueType.FLOAT_LIST, [1.5, 2.3]).to_literal_string()
        assert result == "一又五秒、二又三秒"

    def test_布尔值列表(self):
        assert Value(ValueType.BOOLEAN_LIST, [True, False]).to_literal_string() == "是、否"
