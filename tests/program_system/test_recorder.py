"""测试 zhuziyayan.program_system.recorder — RecordEntry、Recorder 以及执行记录功能。"""

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.expression import VariableExpression
from zhuziyayan.program_system.io_strategy import PythonNativeIO
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.recorder import RecordEntry, Recorder
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
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo
from zhuziyayan.translator.statement_info import StatementInfo


# =============================================================================
# 辅助函数
# =============================================================================


def make_statement_info(statement: str, annotation_ids: list[str] | None = None) -> StatementInfo:
    """创建 StatementInfo 的快捷方式。"""
    if annotation_ids is None:
        annotation_ids = []
    return StatementInfo(statement, annotation_ids)


def make_ctx(**variables: Value) -> Context:
    """创建包含指定变量的 Context。"""
    ctx = Context(None)
    for name, value in variables.items():
        ctx.set_variable(name, value)
    return ctx


def make_program_info(title_name: str = "《测试》", statements: list[str] | None = None) -> ProgramInfo:
    """创建最简 ProgramInfo。"""
    if statements is None:
        statements = []
    stmt_infos = [make_statement_info(s) for s in statements]
    title_func = FunctionInfo(title_name, stmt_infos, {})
    return ProgramInfo(title_func, [])


# =============================================================================
# RecordEntry
# =============================================================================


class TestRecordEntry:
    """RecordEntry 数据类的基本测试。"""

    def test_构造与字段(self):
        entry = RecordEntry(
            statement_description="定义甲子为五",
            change="甲子 = 五",
            statement_name="变量定义",
            details={"变量名": "甲子", "初始值": "五"},
            annotations={"note1": "这是注释"},
        )
        assert entry.statement_description == "定义甲子为五"
        assert entry.change == "甲子 = 五"
        assert entry.statement_name == "变量定义"
        assert entry.details == {"变量名": "甲子", "初始值": "五"}
        assert entry.annotations == {"note1": "这是注释"}

    def test_只读性(self):
        """RecordEntry 是 frozen dataclass，不可修改。"""
        entry = RecordEntry("描述", "变化", "类型")
        try:
            entry.statement_description = "新描述"  # type: ignore[misc]
            assert False, "应该抛出 FrozenInstanceError"
        except Exception:
            pass

    def test_to_string_有变化(self):
        entry = RecordEntry(
            statement_description="定义甲子为五",
            change="甲子 = 五",
            statement_name="变量定义",
            source_code="甲子数五。",
        )
        expected = "【经】甲子数五。\n【注】定义甲子为五\n【疏】甲子 = 五"
        assert entry.to_string() == expected

    def test_to_string_无变化(self):
        entry = RecordEntry(
            statement_description="（无操作）",
            change="",
            statement_name="无操作",
            source_code="某无意义语句。",
        )
        expected = "【经】某无意义语句。\n【注】（无操作）"
        assert entry.to_string() == expected

    def test_to_string_起章(self):
        entry = RecordEntry(
            statement_description="进入函数《测试》",
            change="",
            statement_name="起章",
            details={"函数名": "《测试》"},
        )
        assert entry.to_string() == "起《测试》"

    def test_to_string_毕章(self):
        entry = RecordEntry(
            statement_description="退出函数《测试》",
            change="",
            statement_name="毕章",
            details={"函数名": "《测试》"},
        )
        assert entry.to_string() == "毕《测试》"

    def test_默认字段值(self):
        """details、annotations、source_code 默认是空。"""
        entry = RecordEntry("描述", "变化", "类型")
        assert entry.details == {}
        assert entry.annotations == {}
        assert entry.source_code == ""


# =============================================================================
# Recorder
# =============================================================================


class TestRecorder:
    """Recorder 类的基本测试。"""

    def test_初始为空(self):
        r = Recorder()
        assert r.get_entries() == []
        assert r.get_entries_as_strings() == []

    def test_record_单条(self):
        r = Recorder()
        entry = RecordEntry("描述", "变化", "类型")
        r.record(entry)
        assert len(r.get_entries()) == 1
        assert r.get_entries()[0] is entry

    def test_record_多条(self):
        r = Recorder()
        e1 = RecordEntry("描述1", "变化1", "类型1")
        e2 = RecordEntry("描述2", "变化2", "类型2")
        r.record(e1)
        r.record(e2)
        assert len(r.get_entries()) == 2

    def test_get_entries_返回副本(self):
        """get_entries 返回副本，外部修改不影响内部。"""
        r = Recorder()
        r.record(RecordEntry("描述", "变化", "类型"))
        entries = r.get_entries()
        entries.pop()
        assert len(r.get_entries()) == 1

    def test_get_entries_as_strings(self):
        r = Recorder()
        r.record(RecordEntry("定义甲子为五", "甲子 = 五", "变量定义", source_code="甲子数五。"))
        r.record(RecordEntry("（无操作）", "", "无操作", source_code="某语句。"))
        strings = r.get_entries_as_strings()
        expected_1 = "【经】甲子数五。\n【注】定义甲子为五\n【疏】甲子 = 五"
        expected_2 = "【经】某语句。\n【注】（无操作）"
        assert strings == [expected_1, expected_2]

    def test_get_full_text(self):
        """get_full_text 用空行连接各条目。"""
        r = Recorder()
        r.record(RecordEntry("定义甲子为五", "甲子 = 五", "变量定义", source_code="甲子数五。"))
        r.record(RecordEntry("（无操作）", "", "无操作", source_code="某语句。"))
        text = r.get_full_text()
        assert "\n\n" in text


# =============================================================================
# Program.recorder
# =============================================================================


class TestProgramRecorder:
    """Program 默认创建 Recorder。"""

    def test_默认创建recorder(self):
        info = make_program_info()
        program = Program(info, PythonNativeIO())
        assert isinstance(program.recorder, Recorder)

    def test_recorder可访问且为空(self):
        info = make_program_info()
        program = Program(info, PythonNativeIO())
        assert program.recorder.get_entries() == []


# =============================================================================
# Statement 子类的 name 和 details 属性
# =============================================================================


class TestStatementName:
    """所有 14 种 Statement 子类有正确的 name。"""

    def test_变量定义(self):
        stmt = VariableDefinitionStatement(
            make_statement_info("甲子数五。"), make_ctx(),
            "甲子", Value(ValueType.INTEGER, 5),
        )
        assert stmt.name == "变量定义"

    def test_赋值(self):
        stmt = AssignmentStatement(
            make_statement_info("甲子取乙子。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子", VariableExpression("乙子"),
        )
        assert stmt.name == "赋值"

    def test_计算赋值(self):
        stmt = ComputeAssignmentStatement(
            make_statement_info("甲子益乙子。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子", ComputeOperator.ADD, VariableExpression("乙子"),
        )
        assert stmt.name == "计算赋值"

    def test_判零(self):
        stmt = ZeroCheckStatement(
            make_statement_info("甲子虚。"), make_ctx(甲子=Value(ValueType.INTEGER, 0)),
            "甲子",
        )
        assert stmt.name == "判零"

    def test_判正(self):
        stmt = PositiveCheckStatement(
            make_statement_info("甲子正。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子",
        )
        assert stmt.name == "判正"

    def test_列表索引修改(self):
        stmt = ListIndexModifyStatement(
            make_statement_info("列子易其一曰新子。"),
            make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"])),
            "列子", 1, VariableExpression("新子"),
        )
        assert stmt.name == "列表索引修改"

    def test_列表追加(self):
        stmt = ListAppendStatement(
            make_statement_info("列子接新子。"),
            make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"])),
            "列子", VariableExpression("新子"),
        )
        assert stmt.name == "列表追加"

    def test_列表删尾(self):
        stmt = ListPopTailStatement(
            make_statement_info("列子削。"),
            make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2])),
            "列子",
        )
        assert stmt.name == "列表删尾"

    def test_列表删头(self):
        stmt = ListPopHeadStatement(
            make_statement_info("列子斩。"),
            make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2])),
            "列子",
        )
        assert stmt.name == "列表删头"

    def test_函数调用(self):
        stmt = FunctionCallStatement(
            make_statement_info("甲子行《学而》。"), make_ctx(甲子=Value(ValueType.INTEGER, 1)),
            "学而",
        )
        assert stmt.name == "函数调用"

    def test_条件判断(self):
        stmt = IfStatement(
            make_statement_info("若条件子是则行《学而》。"),
            make_ctx(条件子=Value(ValueType.BOOLEAN, True)),
            "条件子", "学而",
        )
        assert stmt.name == "条件判断"

    def test_输出(self):
        stmt = OutputStatement(
            make_statement_info("甲子曰。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子",
        )
        assert stmt.name == "输出"

    def test_输入(self):
        stmt = InputStatement(
            make_statement_info("甲子问请输入。"), make_ctx(甲子=Value(ValueType.STRING, "")),
            "甲子", "请输入",
        )
        assert stmt.name == "输入"

    def test_无操作(self):
        stmt = LiteraryStatement(make_statement_info(""), Context(None))
        assert stmt.name == "无操作"


# =============================================================================
# Statement 子类的 details 字典
# =============================================================================


class TestStatementDetails:
    """Statement 子类的 details 字典包含正确的键和值。"""

    def test_变量定义_details(self):
        stmt = VariableDefinitionStatement(
            make_statement_info("甲子数五。"), make_ctx(),
            "甲子", Value(ValueType.INTEGER, 5),
        )
        assert stmt.details["变量名"] == "甲子"
        assert stmt.details["类型"] == "整数"
        assert stmt.details["初始值"] == "五"

    def test_赋值_details(self):
        stmt = AssignmentStatement(
            make_statement_info("甲子取乙子。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子", VariableExpression("乙子"),
        )
        assert stmt.details["目标变量"] == "甲子"
        assert stmt.details["来源"] == "乙子"

    def test_计算赋值_details(self):
        stmt = ComputeAssignmentStatement(
            make_statement_info("甲子益乙子。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子", ComputeOperator.ADD, VariableExpression("乙子"),
        )
        assert stmt.details["目标变量"] == "甲子"
        assert stmt.details["运算符"] == "加"
        assert stmt.details["来源"] == "乙子"

    def test_判零_details(self):
        stmt = ZeroCheckStatement(
            make_statement_info("甲子虚。"), make_ctx(甲子=Value(ValueType.INTEGER, 0)),
            "甲子",
        )
        assert stmt.details["目标变量"] == "甲子"

    def test_判正_details(self):
        stmt = PositiveCheckStatement(
            make_statement_info("甲子正。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子",
        )
        assert stmt.details["目标变量"] == "甲子"

    def test_列表索引修改_details(self):
        stmt = ListIndexModifyStatement(
            make_statement_info("列子易其一曰新子。"),
            make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"])),
            "列子", 1, VariableExpression("新子"),
        )
        assert stmt.details["目标变量"] == "列子"
        assert stmt.details["索引"] == "一"
        assert stmt.details["新值"] == "新子"

    def test_列表追加_details(self):
        stmt = ListAppendStatement(
            make_statement_info("列子接新子。"),
            make_ctx(列子=Value(ValueType.STRING_LIST, ["甲"])),
            "列子", VariableExpression("新子"),
        )
        assert stmt.details["目标列表"] == "列子"
        assert stmt.details["追加值"] == "新子"

    def test_函数调用_details(self):
        stmt = FunctionCallStatement(
            make_statement_info("甲子行《学而》。"), make_ctx(甲子=Value(ValueType.INTEGER, 1)),
            "学而",
        )
        assert stmt.details["函数名"] == "学而"

    def test_条件判断_details(self):
        stmt = IfStatement(
            make_statement_info("若条件子是则行《学而》。"),
            make_ctx(条件子=Value(ValueType.BOOLEAN, True)),
            "条件子", "学而",
        )
        assert stmt.details["条件变量"] == "条件子"
        assert stmt.details["调用的函数"] == "学而"

    def test_输出_details(self):
        stmt = OutputStatement(
            make_statement_info("甲子曰。"), make_ctx(甲子=Value(ValueType.INTEGER, 5)),
            "甲子",
        )
        assert stmt.details["输出变量"] == "甲子"

    def test_输入_带提示_details(self):
        stmt = InputStatement(
            make_statement_info("甲子问请输入。"), make_ctx(甲子=Value(ValueType.STRING, "")),
            "甲子", "请输入",
        )
        assert stmt.details["输入变量"] == "甲子"
        assert stmt.details["提示"] == "请输入"

    def test_输入_无提示_details(self):
        stmt = InputStatement(
            make_statement_info("甲子听。"), make_ctx(甲子=Value(ValueType.STRING, "")),
            "甲子",
        )
        assert stmt.details["输入变量"] == "甲子"
        assert "提示" not in stmt.details

    def test_details_返回副本(self):
        """details 返回副本，外部修改不影响内部。"""
        stmt = VariableDefinitionStatement(
            make_statement_info("甲子数五。"), make_ctx(),
            "甲子", Value(ValueType.INTEGER, 5),
        )
        d = stmt.details
        d["新键"] = "新值"
        assert "新键" not in stmt.details


# =============================================================================
# Statement 子类的 describe()
# =============================================================================


class TestStatementDescribe:
    """Statement 子类的 describe() 方法返回正确的描述和变化。"""

    def test_变量定义_describe(self):
        ctx = make_ctx()
        stmt = VariableDefinitionStatement(
            make_statement_info("甲子数五。"), ctx,
            "甲子", Value(ValueType.INTEGER, 5),
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "定义甲子为五"
        assert change == "甲子 = 五 数也"

    def test_赋值_describe(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0), 乙子=Value(ValueType.INTEGER, 5))
        stmt = AssignmentStatement(
            make_statement_info("甲子取乙子。"), ctx,
            "甲子", VariableExpression("乙子"),
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "甲子取乙子"
        assert change == "甲子 = 五 数也"

    def test_计算赋值_describe(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 3), 乙子=Value(ValueType.INTEGER, 2))
        stmt = ComputeAssignmentStatement(
            make_statement_info("甲子益乙子。"), ctx,
            "甲子", ComputeOperator.ADD, VariableExpression("乙子"),
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "甲子加乙子"
        assert change == "甲子 = 五 数也"

    def test_判零_describe_零值(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 0))
        stmt = ZeroCheckStatement(make_statement_info("甲子虚。"), ctx, "甲子")
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "判零甲子"
        assert change == "甲子 = 是 辩也"

    def test_判零_describe_非零值(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        stmt = ZeroCheckStatement(make_statement_info("甲子虚。"), ctx, "甲子")
        stmt.run()
        _, change = stmt.describe()
        assert change == "甲子 = 否 辩也"

    def test_判正_describe_正值(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        stmt = PositiveCheckStatement(make_statement_info("甲子正。"), ctx, "甲子")
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "判正甲子"
        assert change == "甲子 = 是 辩也"

    def test_函数调用_describe(self):
        """函数调用 describe 返回调用描述，change 为空（执行由上层负责）。"""
        stmt = FunctionCallStatement(
            make_statement_info("甲子行《学而》。"), make_ctx(甲子=Value(ValueType.INTEGER, 1)),
            "学而",
        )
        desc, change = stmt.describe()
        assert desc == "调用函数《学而》"
        assert change == ""

    def test_条件判断_describe_条件成立(self):
        ctx = make_ctx(条件子=Value(ValueType.BOOLEAN, True))
        stmt = IfStatement(
            make_statement_info("若条件子是则行《学而》。"), ctx,
            "条件子", "学而",
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "若条件子则调用《学而》"
        assert change == "将调用《学而》"

    def test_条件判断_describe_条件不成立(self):
        ctx = make_ctx(条件子=Value(ValueType.BOOLEAN, False))
        stmt = IfStatement(
            make_statement_info("若条件子是则行《学而》。"), ctx,
            "条件子", "学而",
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "若条件子则调用《学而》"
        assert change == "跳过"

    def test_输出_describe(self):
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        stmt = OutputStatement(make_statement_info("甲子曰。"), ctx, "甲子")
        desc, change = stmt.describe()
        assert desc == "输出甲子"
        assert change == "甲子 = 五 数也"

    def test_无操作_describe(self):
        stmt = LiteraryStatement(make_statement_info(""), Context(None))
        desc, change = stmt.describe()
        assert desc == "（无操作）"
        assert change == ""

    def test_列表追加_describe(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2]), 新子=Value(ValueType.INTEGER, 3))
        stmt = ListAppendStatement(
            make_statement_info("列子接新子。"), ctx,
            "列子", VariableExpression("新子"),
        )
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "列子追加新子"
        assert change == "列子 = 一、二、三 列数也"

    def test_列表删尾_describe(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        stmt = ListPopTailStatement(make_statement_info("列子削。"), ctx, "列子")
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "列子删尾"
        assert change == "列子 = 一、二 列数也"

    def test_列表删头_describe(self):
        ctx = make_ctx(列子=Value(ValueType.INTEGER_LIST, [1, 2, 3]))
        stmt = ListPopHeadStatement(make_statement_info("列子斩。"), ctx, "列子")
        stmt.run()
        desc, change = stmt.describe()
        assert desc == "列子删头"
        assert change == "列子 = 二、三 列数也"

    def test_describe_变量被置None后(self):
        """赋值目标不存在时 run() 将其置为 NONE，describe 应反映此状态。"""
        ctx = make_ctx(甲子=Value(ValueType.INTEGER, 5))
        # 乙子不存在 → run() 将其设为 NONE
        stmt = AssignmentStatement(
            make_statement_info("乙子取甲子。"), ctx,
            "乙子", VariableExpression("甲子"),
        )
        stmt.run()
        _, change = stmt.describe()
        assert change == "乙子 = 无"


# =============================================================================
# Function.execute() 记录集成测试
# =============================================================================


class TestFunctionExecuteRecording:
    """Function.execute() 会向 Recorder 记录执行过程。"""

    def test_标题函数执行记录进入和退出(self):
        """执行最简单的标题函数，应记录进入和退出。"""
        info = make_program_info("《测试》", ["甲子数五。"])
        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        names = [e.statement_name for e in entries]
        assert "起章" in names
        assert "毕章" in names
        assert "变量定义" in names

    def test_记录包含语句描述和变化(self):
        info = make_program_info("《测试》", ["甲子数五。"])
        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        # 找到变量定义条目
        var_def_entry = [e for e in entries if e.statement_name == "变量定义"][0]
        assert var_def_entry.statement_description == "定义甲子为五"
        assert var_def_entry.change == "甲子 = 五 数也"

    def test_程序未运行时抛出异常(self):
        """无 Program 运行时 Function.execute() 应抛出 RuntimeError。"""
        from zhuziyayan.program_system.function import Function
        import pytest
        info = make_program_info("《测试》", ["甲子数五。"])
        func = Function(info.title_function, None)
        with pytest.raises(RuntimeError, match="Program 实例不存在"):
            func.execute()

    def test_进入退出条目details(self):
        info = make_program_info("《测试》", [])
        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        entry_record = [e for e in entries if e.statement_name == "起章"][0]
        assert entry_record.details["函数名"] == "《测试》"

        exit_record = [e for e in entries if e.statement_name == "毕章"][0]
        assert exit_record.details["函数名"] == "《测试》"


# =============================================================================
# 注释解析测试
# =============================================================================


class TestAnnotationRecording:
    """执行时正确解析并记录注释。"""

    def test_注释被解析并记录(self):
        """测试 annotations 从 FunctionInfo.annotations 按 annotation_ids 解析。"""
        annotations = {"注1": "这是注释内容", "注2": "另一条注释"}
        stmt_info = make_statement_info("甲子数五。", annotation_ids=["注1", "注2"])

        title_func = FunctionInfo("《测试》", [stmt_info], annotations)
        info = ProgramInfo(title_func, [])

        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        var_entry = [e for e in entries if e.statement_name == "变量定义"][0]
        assert var_entry.annotations == {"注1": "这是注释内容", "注2": "另一条注释"}

    def test_无注释时annotations为空(self):
        stmt_info = make_statement_info("甲子数五。", annotation_ids=[])
        title_func = FunctionInfo("《测试》", [stmt_info], {})
        info = ProgramInfo(title_func, [])

        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        var_entry = [e for e in entries if e.statement_name == "变量定义"][0]
        assert var_entry.annotations == {}

    def test_注释ID不存在时跳过(self):
        """annotation_id 在 annotations 中不存在时，应跳过。"""
        annotations = {"注1": "存在"}
        stmt_info = make_statement_info("甲子数五。", annotation_ids=["注1", "不存在ID"])
        title_func = FunctionInfo("《测试》", [stmt_info], annotations)
        info = ProgramInfo(title_func, [])

        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        var_entry = [e for e in entries if e.statement_name == "变量定义"][0]
        assert var_entry.annotations == {"注1": "存在"}


# =============================================================================
# 嵌套函数调用记录顺序
# =============================================================================


class TestNestedFunctionCallRecording:
    """嵌套函数调用时记录顺序正确：子函数内部先记录，调用语句后记录。"""

    def test_嵌套调用记录顺序(self):
        """父函数调用子函数 → 子函数进入/语句/退出先记录 → 父函数调用语句后记录。"""
        annotations = {}
        child_stmts = [make_statement_info("丙子数十。")]
        child_func = FunctionInfo("《子篇》", child_stmts, annotations)

        parent_stmts = [
            make_statement_info("甲子数五。"),
            make_statement_info("甲子行《子篇》。"),  # 调用子函数
            make_statement_info("乙子数三。"),
        ]
        title_func = FunctionInfo("《测试》", parent_stmts, annotations)
        info = ProgramInfo(title_func, [child_func])

        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        names = [e.statement_name for e in entries]

        # 期望顺序：
        # 函数进入（测试）→ 变量定义（甲子）→
        #   函数调用 → 函数进入（子篇）→ 变量定义（丙子）→ 函数退出（子篇）→
        #   变量定义（乙子）→ 函数退出（测试）
        assert names == [
            "起章",
            "变量定义",
            "函数调用",
            "起章",
            "变量定义",
            "毕章",
            "变量定义",
            "毕章",
        ]

    def test_嵌套调用_entry_exit配对(self):
        """进入和退出应正确配对。"""
        child_stmts = [make_statement_info("丙子数十。")]
        child_func = FunctionInfo("《子篇》", child_stmts, {})

        # 需要先定义甲子，否则 decide() 会将其识别为变量定义而非函数调用
        parent_stmts = [
            make_statement_info("甲子数十。"),
            make_statement_info("甲子行《子篇》。"),
        ]
        title_func = FunctionInfo("《测试》", parent_stmts, {})
        info = ProgramInfo(title_func, [child_func])

        program = Program(info, PythonNativeIO())
        program.run()

        entries = program.recorder.get_entries()
        # 提取所有进入/退出的函数名
        func_events = [
            (e.statement_name, e.details["函数名"])
            for e in entries
            if e.statement_name in ("起章", "毕章")
        ]
        # 父进入 → 子进入 → 子退出 → 父退出
        assert func_events[0] == ("起章", "《测试》")
        assert func_events[1] == ("起章", "《子篇》")
        assert func_events[2] == ("毕章", "《子篇》")
        assert func_events[3] == ("毕章", "《测试》")


# =============================================================================
# Recorder.get_entries_as_strings 端到端测试
# =============================================================================


class TestRecorderEndToEnd:
    """端到端测试：从程序执行到获取字符串记录。"""

    def test_简单程序的全部字符串记录(self):
        info = make_program_info("《测试》", ["甲子数五。", "乙子数十。"])
        program = Program(info, PythonNativeIO())
        program.run()

        strings = program.recorder.get_entries_as_strings()
        # 顺序：进入 → 变量定义甲子 → 变量定义乙子 → 退出
        assert len(strings) == 4
        # 进入/退出使用简单格式
        assert strings[0] == "起《测试》"
        assert strings[3] == "毕《测试》"
        # 语句使用经注疏格式
        assert "【经】甲子数五。" in strings[1]
        assert "【注】定义甲子为五" in strings[1]
        assert "【疏】甲子 = 五 数也" in strings[1]
        assert "【经】乙子数十。" in strings[2]
        assert "【注】定义乙子为十" in strings[2]
        assert "【疏】乙子 = 十 数也" in strings[2]

    def test_get_full_text端到端(self):
        """get_full_text 返回完整复盘文本。"""
        info = make_program_info("《测试》", ["甲子数五。"])
        program = Program(info, PythonNativeIO())
        program.run()

        text = program.recorder.get_full_text()
        lines = text.split("\n")
        # 函数进入（简单格式）和语句（经注疏格式）之间有空行
        assert "起《测试》" in lines
        assert "【经】甲子数五。" in lines
        assert "毕《测试》" in lines
        # 验证有空行分隔
        assert "\n\n" in text
