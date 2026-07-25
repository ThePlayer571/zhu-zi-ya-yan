"""测试所有 14 种 Statement 子类的 run() 方法。

测试覆盖正常路径和边界情况。
"""

import pytest
import sys
from io import StringIO

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.expression import (
    ListIndexExpression,
    VariableExpression,
)
from zhuziyayan.program_system.statement import (
    AssignmentStatement,
    ComputeAssignmentStatement,
    ComputeOperator,
    FunctionCallStatement,
    IfStatement,
    InputStatement,
    ListAppendStatement,
    ListIndexModifyStatement,
    ListPopHeadStatement,
    ListPopTailStatement,
    LiteraryStatement,
    OutputStatement,
    PositiveCheckStatement,
    VariableDefinitionStatement,
    ZeroCheckStatement,
)
from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.translator.statement_info import StatementInfo


# =============================================================================
# 辅助
# =============================================================================


def make_si(statement: str = "测试。") -> StatementInfo:
    return StatementInfo(statement, [])


def make_ctx(**variables: Value) -> Context:
    ctx = Context(None)
    for name, value in variables.items():
        ctx.set_variable(name, value)
    return ctx


# =============================================================================
# 1. VariableDefinitionStatement
# =============================================================================


class TestVariableDefinitionRun:
    """变量定义语句的执行测试。"""

    def test_定义新变量(self):
        ctx = Context(None)
        stmt = VariableDefinitionStatement(make_si(), ctx, "甲子", Value(ValueType.INTEGER, 42))
        stmt.run()
        assert ctx.has_variable("甲子")
        assert ctx.get_variable("甲子").value.raw == 42

    def test_覆盖已存在变量(self):
        """定义语句也会覆盖已存在变量（通过 set_variable）。"""
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        stmt = VariableDefinitionStatement(make_si(), ctx, "甲子", Value(ValueType.STRING, "new"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.STRING
        assert ctx.get_variable("甲子").value.raw == "new"


# =============================================================================
# 2. AssignmentStatement
# =============================================================================


class TestAssignmentRun:
    """赋值语句的执行测试。"""

    def test_正常赋值(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        stmt = AssignmentStatement(make_si(), ctx, "甲子", VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 10

    def test_目标不存在_置为NONE(self):
        ctx = Context(None)
        stmt = AssignmentStatement(make_si(), ctx, "不存在子", VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("不存在子").value.type == ValueType.NONE

    def test_源为NONE_目标置为NONE(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.NONE, None))
        stmt = AssignmentStatement(make_si(), ctx, "甲子", VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    def test_列表赋值深拷贝(self):
        """列表赋值执行深拷贝，修改原列表不影响赋值后的变量。"""
        original = Value(ValueType.STRING_LIST, ["甲", "乙"])
        ctx = make_ctx(甲子=original, 乙子=Value(ValueType.STRING_LIST, ["丙"]))
        stmt = AssignmentStatement(make_si(), ctx, "乙子", VariableExpression("甲子"))
        stmt.run()
        # 修改原列表
        original.raw.append("新")
        assert ctx.get_variable("乙子").value.raw == ["甲", "乙"]  # 未被影响

    def test_从列表索引赋值(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0), 列子=Value(ValueType.STRING_LIST, ["甲", "乙"]))
        stmt = AssignmentStatement(make_si(), ctx, "甲子", ListIndexExpression("列子", 1))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.STRING
        assert ctx.get_variable("甲子").value.raw == "甲"


# =============================================================================
# 3. ComputeAssignmentStatement
# =============================================================================


class TestComputeAssignmentRun:
    """计算赋值语句的执行测试。"""

    # ---- INTEGER ----

    def test_整数加法(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 3))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 8

    def test_整数减法(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 10), 乙子=Value(ValueType.INTEGER, 3))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.SUB, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 7

    def test_整数减法_结果为负_截断为零(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 3), 乙子=Value(ValueType.INTEGER, 10))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.SUB, VariableExpression("乙子"))
        stmt.run()
        # raw 会是 -7 → Variable.set_value 中 clamp_if_negative 截断为 0
        assert ctx.get_variable("甲子").value.raw == 0

    def test_整数乘法(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 3))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.MUL, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 15

    def test_整数除法_地板除(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 10), 乙子=Value(ValueType.INTEGER, 3))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.DIV, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 3  # 10 // 3

    def test_整数取模(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 10), 乙子=Value(ValueType.INTEGER, 3))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.MOD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 1

    # ---- FLOAT ----

    def test_浮点数加法(self):
        ctx = make_ctx(甲子=Value(ValueType.FLOAT, 2.5), 乙子=Value(ValueType.FLOAT, 1.5))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == 4.0

    def test_浮点数除法_真除(self):
        ctx = make_ctx(甲子=Value(ValueType.FLOAT, 10.0), 乙子=Value(ValueType.FLOAT, 3.0))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.DIV, VariableExpression("乙子"))
        stmt.run()
        assert abs(ctx.get_variable("甲子").value.raw - 10.0 / 3.0) < 0.0001

    # ---- STRING ----

    def test_字符串连接(self):
        ctx = make_ctx(甲子=Value(ValueType.STRING, "hello"), 乙子=Value(ValueType.STRING, " world"))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == "hello world"

    def test_字符串不支持减法(self):
        """字符串减法会导致变量被置为 NONE。"""
        ctx = make_ctx(甲子=Value(ValueType.STRING, "hello"), 乙子=Value(ValueType.STRING, "world"))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.SUB, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    # ---- BOOLEAN ----

    def test_布尔加法_逻辑或(self):
        ctx = make_ctx(甲子=Value(ValueType.BOOLEAN, True), 乙子=Value(ValueType.BOOLEAN, False))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        # True + False → bool(1 + 0) = True
        assert ctx.get_variable("甲子").value.raw is True

    # ---- LIST ----

    def test_列表连接(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER_LIST, [1, 2]), 乙子=Value(ValueType.INTEGER_LIST, [3, 4]))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.raw == [1, 2, 3, 4]

    # ---- 边界情况 ----

    def test_目标不存在_置为NONE(self):
        ctx = Context(None)
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    def test_源为NONE_目标置为NONE(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.NONE, None))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    def test_类型不匹配_置为NONE(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.FLOAT, 3.0))
        stmt = ComputeAssignmentStatement(make_si(), ctx, "甲子", ComputeOperator.ADD, VariableExpression("乙子"))
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE


# =============================================================================
# 4. ZeroCheckStatement
# =============================================================================


class TestZeroCheckRun:
    """判零语句的执行测试。"""

    def test_整数零_返回True(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0))
        ZeroCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.type == ValueType.BOOLEAN
        assert ctx.get_variable("甲子").value.raw is True

    def test_整数非零_返回False(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        ZeroCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.raw is False

    def test_空字符串_返回True(self):
        ctx = make_ctx(甲子=Value(ValueType.STRING, ""))
        ZeroCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.raw is True

    def test_不存在变量_置为NONE(self):
        ctx = Context(None)
        ZeroCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE


# =============================================================================
# 5. PositiveCheckStatement
# =============================================================================


class TestPositiveCheckRun:
    """判正语句的执行测试。"""

    def test_整数零_返回False(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0))
        PositiveCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.raw is False

    def test_整数正_返回True(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        PositiveCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.raw is True

    def test_不存在变量_置为NONE(self):
        ctx = Context(None)
        PositiveCheckStatement(make_si(), ctx, "甲子").run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE


# =============================================================================
# 6. ListIndexModifyStatement
# =============================================================================


class TestListIndexModifyRun:
    """列表索引修改语句的执行测试。"""

    def test_正常修改(self):
        ctx = make_ctx(列子=Value(ValueType.STRING_LIST, ["甲", "乙", "丙"]), 新子=Value(ValueType.STRING, "丁"))
        ListIndexModifyStatement(make_si(), ctx, "列子", 2, VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.raw == ["甲", "丁", "丙"]

    def test_索引越界_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2]), 新子=Value(ValueType.INTEGER, 3))
        ListIndexModifyStatement(make_si(), ctx, "列子", 5, VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE

    def test_类型不匹配_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2]), 新子=Value(ValueType.STRING, "hello"))
        ListIndexModifyStatement(make_si(), ctx, "列子", 1, VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE

    def test_源为NONE_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"]), 新子=Value(ValueType.NONE, None))
        ListIndexModifyStatement(make_si(), ctx, "列子", 1, VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE

    def test_目标不存在_置为NONE(self):
        ctx = make_ctx(新子=Value(ValueType.STRING, "甲"))
        ListIndexModifyStatement(make_si(), ctx, "列子", 1, VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE


# =============================================================================
# 7. ListAppendStatement
# =============================================================================


class TestListAppendRun:
    """列表追加语句的执行测试。"""

    def test_正常追加(self):
        ctx = make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"]), 新子=Value(ValueType.STRING, "乙"))
        ListAppendStatement(make_si(), ctx, "列子", VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.raw == ["甲", "乙"]

    def test_类型不匹配_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1]), 新子=Value(ValueType.STRING, "oops"))
        ListAppendStatement(make_si(), ctx, "列子", VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE

    def test_目标不存在_置为NONE(self):
        ctx = make_ctx(新子=Value(ValueType.STRING, "甲"))
        ListAppendStatement(make_si(), ctx, "列子", VariableExpression("新子")).run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE


# =============================================================================
# 8. ListPopTailStatement
# =============================================================================


class TestListPopTailRun:
    """列表删尾语句的执行测试。"""

    def test_正常删尾(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        ListPopTailStatement(make_si(), ctx, "列子").run()
        assert ctx.get_variable("列子").value.raw == [1, 2]

    def test_空列表删尾_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.STRING_LIST, []))
        ListPopTailStatement(make_si(), ctx, "列子").run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE

    def test_目标不存在_置为NONE(self):
        ctx = Context(None)
        ListPopTailStatement(make_si(), ctx, "列子").run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE


# =============================================================================
# 9. ListPopHeadStatement
# =============================================================================


class TestListPopHeadRun:
    """列表删头语句的执行测试。"""

    def test_正常删头(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        ListPopHeadStatement(make_si(), ctx, "列子").run()
        assert ctx.get_variable("列子").value.raw == [2, 3]

    def test_空列表删头_置为NONE(self):
        ctx = make_ctx(列子=Value(ValueType.STRING_LIST, []))
        ListPopHeadStatement(make_si(), ctx, "列子").run()
        assert ctx.get_variable("列子").value.type == ValueType.NONE


# =============================================================================
# 10. FunctionCallStatement
# =============================================================================


class TestFunctionCallRun:
    """函数调用语句的执行测试。

    注：FunctionCallStatement.run() 仅返回函数名，由上层 Function.execute() 负责
    检查 Program 并执行实际调用。
    """

    def test_run返回函数名(self):
        """run() 返回需要调用的函数名。"""
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0))
        stmt = FunctionCallStatement(make_si(), ctx, "学而")
        assert stmt.run() == "学而"


# =============================================================================
# 11. IfStatement
# =============================================================================


class TestIfStatementRun:
    """If 条件语句的执行测试。"""

    def test_条件变量不存在_静默跳过(self):
        ctx = Context(None)
        stmt = IfStatement(make_si(), ctx, "条件子", "学而")
        # 不应抛出异常
        stmt.run()

    def test_条件非布尔类型_静默跳过(self):
        ctx = make_ctx(条件子=Value(ValueType.INTEGER, 1))
        stmt = IfStatement(make_si(), ctx, "条件子", "学而")
        stmt.run()  # 不抛异常

    def test_条件为False_静默跳过(self):
        ctx = make_ctx(条件子=Value(ValueType.BOOLEAN, False))
        stmt = IfStatement(make_si(), ctx, "条件子", "学而")
        stmt.run()  # 不抛异常，不调用函数

    def test_条件为True_run返回函数名(self):
        """条件为 True 时 run() 返回函数名（不直接调用，由上层负责）。"""
        ctx = make_ctx(条件子=Value(ValueType.BOOLEAN, True))
        stmt = IfStatement(make_si(), ctx, "条件子", "学而")
        assert stmt.run() == "学而"


# =============================================================================
# 12. OutputStatement
# =============================================================================


class TestOutputStatementRun:
    """输出语句的执行测试。"""

    def test_变量不存在_静默跳过(self):
        ctx = Context(None)
        stmt = OutputStatement(make_si(), ctx, "甲子")
        stmt.run()  # 不抛异常

    def test_无Program运行时抛出RuntimeError(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        stmt = OutputStatement(make_si(), ctx, "甲子")
        with pytest.raises(RuntimeError):
            stmt.run()


# =============================================================================
# 13. InputStatement
# =============================================================================


class TestInputStatementRun:
    """输入语句的执行测试。"""

    def test_变量不存在_置为NONE(self):
        ctx = Context(None)
        stmt = InputStatement(make_si(), ctx, "甲子")
        stmt.run()
        assert ctx.get_variable("甲子").value.type == ValueType.NONE

    def test_无Program运行时抛出RuntimeError(self):
        ctx = make_ctx(甲子=Value(ValueType.STRING, ""))
        stmt = InputStatement(make_si(), ctx, "甲子")
        with pytest.raises(RuntimeError):
            stmt.run()


# =============================================================================
# 14. LiteraryStatement
# =============================================================================


class TestLiteraryStatementRun:
    """文学性语句的执行测试。"""

    def test_run_无操作(self):
        ctx = Context(None)
        stmt = LiteraryStatement(make_si("莫名其妙的语句。"), ctx)
        stmt.run()  # 不抛任何异常，无副作用


# =============================================================================
# 错误不抛出 — 核心约定
# =============================================================================


class TestNoThrowGuarantee:
    """验证 Statement 永不抛出异常的约定（除 Programming Error 场景外）。"""

    def test_所有正常语句不抛异常(self):
        """在合理的上下文中，任何正常构造的语句都不抛异常。
        各操作用独立的变量新鲜上下文，避免 NONE 级联导致 AttributeError。"""
        # 每个操作用独立上下文避免级联 NONE

        # 变量定义 - 不抛
        ctx1 = Context(None)
        VariableDefinitionStatement(make_si(), ctx1, "新子", Value(ValueType.INTEGER, 1)).run()

        # 赋值 - 不抛
        ctx2 = make_ctx(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        AssignmentStatement(make_si(), ctx2, "甲子", VariableExpression("乙子")).run()

        # 计算赋值 - 类型不匹配也静默置 NONE（不抛）
        ctx3 = make_ctx(甲子=Value(ValueType.INTEGER, 5), 列子=Value(ValueType.STRING_LIST, ["a"]))
        ComputeAssignmentStatement(make_si(), ctx3, "甲子", ComputeOperator.ADD, VariableExpression("列子")).run()

        # 判零 - 不抛
        ctx4 = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        ZeroCheckStatement(make_si(), ctx4, "甲子").run()

        # 判正 - 不抛
        ctx5 = make_ctx(乙子=Value(ValueType.INTEGER, 10))
        PositiveCheckStatement(make_si(), ctx5, "乙子").run()

        # 列表索引修改 - 越界不抛（置 NONE）
        ctx6 = make_ctx(列子=Value(ValueType.STRING_LIST, ["甲", "乙"]), 言子=Value(ValueType.STRING, "hello"))
        ListIndexModifyStatement(make_si(), ctx6, "列子", 99, VariableExpression("言子")).run()

        # 列表追加 - 类型不匹配不抛（置 NONE）
        ctx7 = make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"]), 乙子=Value(ValueType.INTEGER, 10))
        ListAppendStatement(make_si(), ctx7, "列子", VariableExpression("乙子")).run()

        # 删尾 - 不抛
        ctx8 = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        ListPopTailStatement(make_si(), ctx8, "列子").run()

        # 删头 - 不抛
        ctx9 = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        ListPopHeadStatement(make_si(), ctx9, "列子").run()

        # 文学语句 - 不抛
        ctx10 = Context(None)
        LiteraryStatement(make_si(), ctx10).run()
