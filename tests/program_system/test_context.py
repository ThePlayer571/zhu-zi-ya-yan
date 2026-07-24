"""测试 zhuziyayan.program_system.context — Context 类。"""

import pytest
from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.value import Value, ValueType


class TestContextRoot:
    """根 Context（无全局上下文）的单元测试。"""

    def test_新建上下文无变量(self):
        ctx = Context(None)
        assert ctx.has_variable("甲子") is False

    def test_设置后存在(self):
        ctx = Context(None)
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        assert ctx.has_variable("甲子") is True

    def test_获取变量(self):
        ctx = Context(None)
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        v = ctx.get_variable("甲子")
        assert v.name == "甲子"
        assert v.value.raw == 5

    def test_获取不存在变量抛出KeyError(self):
        ctx = Context(None)
        with pytest.raises(KeyError):
            ctx.get_variable("不存在子")

    def test_设置已存在变量更新值(self):
        """设置已存在的变量名时原地更新值，保留 Variable 对象引用。"""
        ctx = Context(None)
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        v1 = ctx.get_variable("甲子")
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 10))
        v2 = ctx.get_variable("甲子")
        assert v1 is v2  # 同一引用
        assert v2.value.raw == 10

    def test_set_to_none(self):
        ctx = Context(None)
        ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        ctx.set_to_none("甲子")
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    def test_set_to_none_不存在的变量自动创建(self):
        ctx = Context(None)
        ctx.set_to_none("甲子")
        assert ctx.has_variable("甲子") is True
        assert ctx.get_variable("甲子").value.type == ValueType.NONE


class TestContextNested:
    """嵌套 Context 的单元测试。"""

    def test_全局上下文变量可读(self):
        """局部上下文没有的变量向上查找到全局。"""
        global_ctx = Context(None)
        global_ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        local_ctx = Context(global_ctx)
        assert local_ctx.has_variable("甲子") is True
        assert local_ctx.get_variable("甲子").value.raw == 5

    def test_局部写回全局(self):
        """局部上下文无同名变量但全局有时，set_variable 委托到全局（写回语义）。"""
        global_ctx = Context(None)
        global_ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        local_ctx = Context(global_ctx)
        local_ctx.set_variable("甲子", Value(ValueType.INTEGER, 10))
        # 写回全局：全局也被修改
        assert local_ctx.get_variable("甲子").value.raw == 10
        assert global_ctx.get_variable("甲子").value.raw == 10

    def test_局部无变量_全局有_更新写回全局(self):
        """局部上下文没有该变量但全局有时，set_variable 委托到全局。"""
        global_ctx = Context(None)
        global_ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        local_ctx = Context(global_ctx)
        local_ctx.set_variable("甲子", Value(ValueType.INTEGER, 20))
        assert global_ctx.get_variable("甲子").value.raw == 20

    def test_局部新建变量不影响全局(self):
        global_ctx = Context(None)
        local_ctx = Context(global_ctx)
        local_ctx.set_variable("甲子", Value(ValueType.INTEGER, 5))
        assert local_ctx.has_variable("甲子") is True
        assert global_ctx.has_variable("甲子") is False

    def test_多层嵌套(self):
        """三层嵌套上下文。"""
        root = Context(None)
        root.set_variable("根", Value(ValueType.INTEGER, 1))
        mid = Context(root)
        mid.set_variable("中", Value(ValueType.INTEGER, 2))
        leaf = Context(mid)
        leaf.set_variable("叶", Value(ValueType.INTEGER, 3))

        assert leaf.get_variable("叶").value.raw == 3
        assert leaf.get_variable("中").value.raw == 2
        assert leaf.get_variable("根").value.raw == 1

    def test_多层嵌套_修改中间层变量从叶子层(self):
        root = Context(None)
        root.set_variable("根", Value(ValueType.INTEGER, 1))
        mid = Context(root)
        mid.set_variable("中", Value(ValueType.INTEGER, 2))
        leaf = Context(mid)

        # 叶子层修改"中"（存在于 mid，不存在于 leaf）
        leaf.set_variable("中", Value(ValueType.INTEGER, 20))
        assert mid.get_variable("中").value.raw == 20
        assert leaf.get_variable("中").value.raw == 20
