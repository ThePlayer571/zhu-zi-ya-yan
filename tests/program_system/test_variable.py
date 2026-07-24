"""测试 zhuziyayan.program_system.variable — Variable 类。"""

from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.program_system.variable import Variable


class TestVariable:
    """Variable 的单元测试。"""

    def test_构造与属性(self):
        v = Variable("甲子", Value(ValueType.INTEGER, 5))
        assert v.name == "甲子"
        assert v.type == ValueType.INTEGER
        assert v.value.raw == 5

    def test_set_value_更新值(self):
        v = Variable("甲子", Value(ValueType.INTEGER, 5))
        v.set_value(Value(ValueType.INTEGER, 10))
        assert v.value.raw == 10

    def test_set_value_可改变类型(self):
        v = Variable("甲子", Value(ValueType.INTEGER, 5))
        v.set_value(Value(ValueType.STRING, "hello"))
        assert v.type == ValueType.STRING
        assert v.value.raw == "hello"

    def test_set_value_自动截断负数(self):
        """设置负整数时自动截断为 0。"""
        v = Variable("甲子", Value(ValueType.INTEGER, 5))
        v.set_value(Value(ValueType.INTEGER, -10))
        assert v.value.raw == 0

    def test_set_value_自动截断负浮点数(self):
        v = Variable("甲子", Value(ValueType.FLOAT, 3.14))
        v.set_value(Value(ValueType.FLOAT, -1.5))
        assert v.value.raw == 0.0

    def test_构造时也截断负数(self):
        """构造 Variable 时就传入负值，也应被截断。"""
        v = Variable("甲子", Value(ValueType.INTEGER, -5))
        assert v.value.raw == 0
