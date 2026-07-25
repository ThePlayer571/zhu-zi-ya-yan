"""测试 zhuziyayan.program_system.function — Function 类。"""

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.function import Function
from zhuziyayan.program_system.io_strategy import PythonNativeIO
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo
from zhuziyayan.translator.statement_info import StatementInfo


def make_func_info(name: str = "《测试》", statements: list[StatementInfo] | None = None) -> FunctionInfo:
    """创建 FunctionInfo 的快捷方式。"""
    return FunctionInfo(name, statements or [], {})


def _run_in_program(func_info: FunctionInfo) -> Program:
    """以 func_info 为书名函数创建并运行 Program。"""
    program = Program(ProgramInfo(func_info, []), PythonNativeIO())
    program.run()
    return program


class TestFunction:
    """Function 的单元测试。"""

    def test_构造和属性(self):
        info = make_func_info("《学而》")
        func = Function(info, None)
        assert func.info is info
        assert isinstance(func.context, Context)

    def test_有外部上下文(self):
        """创建 Function 时传入 external_context。"""
        global_ctx = Context(None)
        global_ctx.set_variable("全局子", Value(ValueType.INTEGER, 1))
        info = make_func_info()
        func = Function(info, global_ctx)
        # 可以访问全局上下文中的变量
        assert func.context.has_variable("全局子")
        assert func.context.get_variable("全局子").value.raw == 1

    def test_无外部上下文(self):
        """传入 None 作为 external_context 创建根作用域。"""
        info = make_func_info()
        func = Function(info, None)
        assert func.context.has_variable("任意子") is False

    def test_execute_空函数体(self):
        info = make_func_info("《空》", [])
        _run_in_program(info)  # 不抛异常

    def test_execute_变量定义语句(self):
        """执行包含变量定义语句的函数。"""
        info = make_func_info("《测试》", [
            StatementInfo("甲子数十。", []),
        ])
        func = Function(info, None)
        # 手动设置 Program._running，因为 execute() 需要它
        program = Program(ProgramInfo(info, []), PythonNativeIO())
        Program._running = program
        try:
            func.execute()
        finally:
            Program._running = None
        assert func.context.has_variable("甲子")
        assert func.context.get_variable("甲子").value.raw == 10

    def test_execute_多条语句顺序执行(self):
        """多条语句按顺序执行，后面的语句可以看到前面的效果。"""
        info = make_func_info("《测试》", [
            StatementInfo("甲子数五。", []),
            StatementInfo("乙子数三。", []),
            StatementInfo("甲子益乙子。", []),  # 甲 += 乙
        ])
        func = Function(info, None)
        program = Program(ProgramInfo(info, []), PythonNativeIO())
        Program._running = program
        try:
            func.execute()
        finally:
            Program._running = None
        assert func.context.get_variable("甲子").value.raw == 8

    def test_execute_文学语句被静默跳过(self):
        """无法解析的语句不影响函数执行。"""
        info = make_func_info("《测试》", [
            StatementInfo("甲子数十。", []),
            StatementInfo("莫名其妙的内容。", []),
            StatementInfo("乙子数零。", []),  # 先定义乙子
            StatementInfo("乙子取甲子。", []),  # 再赋值
        ])
        func = Function(info, None)
        program = Program(ProgramInfo(info, []), PythonNativeIO())
        Program._running = program
        try:
            func.execute()
        finally:
            Program._running = None
        assert func.context.get_variable("甲子").value.raw == 10
        # 乙子 = 甲子（10）
        assert func.context.get_variable("乙子").value.raw == 10
