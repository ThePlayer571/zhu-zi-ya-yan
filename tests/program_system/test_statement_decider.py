"""测试 zhuziyayan.program_system.statement_decider — decide() 和全部解析辅助函数。

覆盖所有 14 种语句类型的解析路由。
"""

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
    Statement,
    VariableDefinitionStatement,
    ZeroCheckStatement,
)
from zhuziyayan.program_system.statement_decider import decide
from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.translator.statement_info import StatementInfo


# =============================================================================
# 辅助函数
# =============================================================================


def make_statement_info(statement: str) -> StatementInfo:
    """创建 StatementInfo 的快捷方式。"""
    return StatementInfo(statement, [])


def make_context_with(**variables: Value) -> Context:
    """创建包含指定变量的 Context。"""
    ctx = Context(None)
    for name, value in variables.items():
        ctx.set_variable(name, value)
    return ctx


# =============================================================================
# LiteraryStatement — 无法解析的兜底
# =============================================================================


class TestLiteraryFallback:
    """decide 在无法解析时返回 LiteraryStatement。"""

    def test_空文本(self):
        result = decide(make_statement_info(""), Context(None))
        assert isinstance(result, LiteraryStatement)

    def test_无子后缀的文本(self):
        result = decide(make_statement_info("普通文本。"), Context(None))
        assert isinstance(result, LiteraryStatement)

    def test_未知变量且无法匹配任何定义模式(self):
        result = decide(make_statement_info("未知词。"), Context(None))
        assert isinstance(result, LiteraryStatement)

    def test_不抛异常_任意输入(self):
        """任意乱码都不抛出异常。"""
        result = decide(make_statement_info("!@#$%^&*()乱码字。"), Context(None))
        assert isinstance(result, Statement)


# =============================================================================
# VariableDefinitionStatement — 变量定义（6 种类型）
# =============================================================================


class TestVariableDefinition:
    """测试变量定义的六种类型路由。"""

    # ---- 字符串定义（独立：曰/云） ----

    def test_字符串_独立_曰(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子曰善。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.variable_name == "甲子"
        assert result.value.type == ValueType.STRING
        assert result.value.raw == "善"

    def test_字符串_独立_云(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子云善。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.STRING
        assert result.value.raw == "善"

    # ---- 字符串定义（搭配：文/言/语/诗…作/书/述/吟） ----

    def test_字符串_搭配_文作(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子文作善。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.STRING
        assert result.value.raw == "善"

    def test_字符串_搭配_言述(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子言述善。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.raw == "善"

    def test_字符串_搭配_诗吟(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子诗吟善。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.raw == "善"

    # ---- 整数定义 ----

    def test_整数定义(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子数一百二十三。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.INTEGER
        assert result.value.raw == 123

    # ---- 浮点数定义 ----

    def test_浮点数定义(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子度曰三又一秒。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.FLOAT
        assert abs(result.value.raw - 3.1) < 0.0001

    def test_浮点数定义_量(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子量曰五。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.FLOAT
        assert result.value.raw == 5.0

    # ---- 布尔值定义 ----

    def test_布尔定义_是(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子辩曰是。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.BOOLEAN
        assert result.value.raw is True

    def test_布尔定义_非(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子判为非。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.raw is False

    def test_布尔定义_是非关键字(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子是非曰然。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.raw is True

    # ---- 列表定义 ----

    def test_列表定义_字符串列表(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子举言元素甲、元素乙。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.STRING_LIST
        assert result.value.raw == ["元素甲", "元素乙"]

    def test_列表定义_整数列表(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子列数一、二、三。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.variable_name == "甲子"
        assert result.value.type == ValueType.INTEGER_LIST
        assert result.value.raw == [1, 2, 3]

    def test_列表定义_浮点数列表(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子举度一又五秒、二又三秒。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.FLOAT_LIST
        assert len(result.value.raw) == 2
        assert abs(result.value.raw[0] - 1.5) < 0.0001

    def test_列表定义_布尔值列表(self):
        ctx = Context(None)
        result = decide(make_statement_info("甲子列判是、否。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.BOOLEAN_LIST
        assert result.value.raw == [True, False]

    def test_列表定义_空列表(self):
        """空列表：举/列+类型字后紧跟一句读（非顿号）。"""
        ctx = Context(None)
        result = decide(make_statement_info("甲子举言。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.STRING_LIST
        assert result.value.raw == []

    # ---- 所有类型不匹配 → NONE ----

    def test_定义失败_降级为NONE(self):
        """无法匹配任何类型定义时初始化为 NONE。"""
        ctx = Context(None)
        result = decide(make_statement_info("新变子莫名其妙。"), ctx)
        assert isinstance(result, VariableDefinitionStatement)
        assert result.value.type == ValueType.NONE


# =============================================================================
# AssignmentStatement — 赋值
# =============================================================================


class TestAssignmentRouting:
    """赋值语句的解析路由测试。"""

    def test_赋值_取(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子取乙子。"), ctx)
        assert isinstance(result, AssignmentStatement)
        assert result.target_variable_name == "甲子"
        assert isinstance(result.source, VariableExpression)
        assert result.source.variable_name == "乙子"

    def test_赋值_为(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子为乙子。"), ctx)
        assert isinstance(result, AssignmentStatement)

    def test_赋值_从列表索引(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        result = decide(make_statement_info("甲子取列子其二。"), ctx)
        assert isinstance(result, AssignmentStatement)
        assert isinstance(result.source, ListIndexExpression)


# =============================================================================
# ComputeAssignmentStatement — 计算赋值
# =============================================================================


class TestComputeAssignmentRouting:
    """计算赋值语句的解析路由测试。"""

    def test_计算赋值加(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子益乙子。"), ctx)
        assert isinstance(result, ComputeAssignmentStatement)
        assert result.operator == ComputeOperator.ADD

    def test_计算赋值减(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子损乙子。"), ctx)
        assert isinstance(result, ComputeAssignmentStatement)
        assert result.operator == ComputeOperator.SUB

    def test_计算赋值乘(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子倍乙子。"), ctx)
        assert isinstance(result, ComputeAssignmentStatement)
        assert result.operator == ComputeOperator.MUL

    def test_计算赋值除(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子分乙子。"), ctx)
        assert isinstance(result, ComputeAssignmentStatement)
        assert result.operator == ComputeOperator.DIV

    def test_计算赋值模(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5), 乙子=Value(ValueType.INTEGER, 10))
        result = decide(make_statement_info("甲子余乙子。"), ctx)
        assert isinstance(result, ComputeAssignmentStatement)
        assert result.operator == ComputeOperator.MOD


# =============================================================================
# ZeroCheckStatement & PositiveCheckStatement — 判零/判正
# =============================================================================


class TestZeroPositiveRouting:
    """判零判正语句的解析路由测试。"""

    def test_判零_虚(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 0))
        result = decide(make_statement_info("甲子虚。"), ctx)
        assert isinstance(result, ZeroCheckStatement)

    def test_判零_空(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, ""))
        result = decide(make_statement_info("甲子空。"), ctx)
        assert isinstance(result, ZeroCheckStatement)

    def test_判零_阴(self):
        ctx = make_context_with(甲子=Value(ValueType.BOOLEAN, False))
        result = decide(make_statement_info("甲子阴。"), ctx)
        assert isinstance(result, ZeroCheckStatement)

    def test_判正_正(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5))
        result = decide(make_statement_info("甲子正。"), ctx)
        assert isinstance(result, PositiveCheckStatement)

    def test_判正_善(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, "hello"))
        result = decide(make_statement_info("甲子善。"), ctx)
        assert isinstance(result, PositiveCheckStatement)

    def test_判正_阳(self):
        ctx = make_context_with(甲子=Value(ValueType.BOOLEAN, True))
        result = decide(make_statement_info("甲子阳。"), ctx)
        assert isinstance(result, PositiveCheckStatement)


# =============================================================================
# 列表操作 — 追加、删尾、删头、索引修改
# =============================================================================


class TestListOperationRouting:
    """列表操作语句的解析路由测试。"""

    def test_追加_接(self):
        ctx = make_context_with(列子=Value(ValueType.STRING_LIST, ["甲"]), 新子=Value(ValueType.STRING, "乙"))
        result = decide(make_statement_info("列子接新子。"), ctx)
        assert isinstance(result, ListAppendStatement)

    def test_追加_增(self):
        ctx = make_context_with(列子=Value(ValueType.STRING_LIST, ["甲"]), 新子=Value(ValueType.STRING, "乙"))
        result = decide(make_statement_info("列子增新子。"), ctx)
        assert isinstance(result, ListAppendStatement)

    def test_删尾(self):
        ctx = make_context_with(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        result = decide(make_statement_info("列子削。"), ctx)
        assert isinstance(result, ListPopTailStatement)

    def test_删头(self):
        ctx = make_context_with(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        result = decide(make_statement_info("列子斩。"), ctx)
        assert isinstance(result, ListPopHeadStatement)

    def test_索引修改(self):
        ctx = make_context_with(列子=Value(ValueType.STRING_LIST, ["甲", "乙"]), 新子=Value(ValueType.STRING, "丙"))
        result = decide(make_statement_info("列子易其一曰新子。"), ctx)
        assert isinstance(result, ListIndexModifyStatement)
        assert result.index == 1


# =============================================================================
# FunctionCallStatement — 函数调用
# =============================================================================


class TestFunctionCallRouting:
    """函数调用语句的解析路由测试。"""

    def test_函数调用_行(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 1))
        result = decide(make_statement_info("甲子行《学而》。"), ctx)
        assert isinstance(result, FunctionCallStatement)
        assert result.function_name == "学而"

    def test_函数调用_用(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 1))
        result = decide(make_statement_info("甲子用《为政》。"), ctx)
        assert isinstance(result, FunctionCallStatement)
        assert result.function_name == "为政"


# =============================================================================
# IfStatement — 条件控制流
# =============================================================================


class TestIfStatementRouting:
    """If 语句的解析路由测试。"""

    def test_基本if(self):
        ctx = make_context_with(条件子=Value(ValueType.BOOLEAN, True))
        result = decide(make_statement_info("若条件子是则行《学而》。"), ctx)
        assert isinstance(result, IfStatement)
        assert result.condition_variable_name == "条件子"
        assert result.function_name == "学而"

    def test_if_苟关键字(self):
        ctx = make_context_with(条件子=Value(ValueType.BOOLEAN, True))
        result = decide(make_statement_info("苟条件子然则行《学而》。"), ctx)
        assert isinstance(result, IfStatement)
        assert result.condition_variable_name == "条件子"

    def test_if_即关键字(self):
        ctx = make_context_with(条件子=Value(ValueType.BOOLEAN, True))
        result = decide(make_statement_info("若条件子真即行《学而》。"), ctx)
        assert isinstance(result, IfStatement)

    def test_if关键字不在子之前_不识别为if(self):
        """if 关键字必须出现在第一个"子"之前才被识别为 if 语句。"""
        ctx = make_context_with(某条件子=Value(ValueType.BOOLEAN, True))
        result = decide(make_statement_info("某条件子若真则行《学而》。"), ctx)
        assert not isinstance(result, IfStatement)


# =============================================================================
# OutputStatement — 输出
# =============================================================================


class TestOutputRouting:
    """输出语句的解析路由测试。"""

    def test_输出_曰(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5))
        result = decide(make_statement_info("甲子曰。"), ctx)
        assert isinstance(result, OutputStatement)
        assert result.target_variable_name == "甲子"

    def test_输出_言(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, "hello"))
        result = decide(make_statement_info("甲子言。"), ctx)
        assert isinstance(result, OutputStatement)

    def test_输出_谓宣吟(self):
        """其他输出关键字。"""
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 5))
        for kw in ("谓", "宣", "吟"):
            result = decide(make_statement_info(f"甲子{kw}。"), ctx)
            assert isinstance(result, OutputStatement), f"关键字'{kw}'未被识别为输出"


# =============================================================================
# InputStatement — 输入
# =============================================================================


class TestInputRouting:
    """输入语句的解析路由测试。"""

    def test_输入_带提示_问(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, ""))
        result = decide(make_statement_info("甲子问请输入。"), ctx)
        assert isinstance(result, InputStatement)
        assert result.target_variable_name == "甲子"
        assert result.prompt == "请输入"

    def test_输入_带提示_询(self):
        ctx = make_context_with(甲子=Value(ValueType.INTEGER, 0))
        result = decide(make_statement_info("甲子询请输入数字。"), ctx)
        assert isinstance(result, InputStatement)
        assert result.prompt == "请输入数字"

    def test_输入_无提示_听(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, ""))
        result = decide(make_statement_info("甲子听。"), ctx)
        assert isinstance(result, InputStatement)
        assert result.prompt is None

    def test_输入_无提示_闻(self):
        ctx = make_context_with(甲子=Value(ValueType.STRING, ""))
        result = decide(make_statement_info("甲子闻。"), ctx)
        assert isinstance(result, InputStatement)
        assert result.prompt is None
