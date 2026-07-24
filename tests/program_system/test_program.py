"""测试 zhuziyayan.program_system.program — Program 类和端到端集成测试。"""

import sys
from io import StringIO
from unittest.mock import MagicMock

import pytest

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.io_strategy import IOStrategy
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo
from zhuziyayan.translator.statement_info import StatementInfo
from zhuziyayan.translator.translator import translate_program


# =============================================================================
# Mock IOStrategy — 用于测试的 IO 桩
# =============================================================================


class MockIO(IOStrategy):
    """测试用 IO 策略：可预设输入和收集输出。"""

    def __init__(self, inputs: list[str] | None = None):
        self.inputs = inputs or []
        self._input_index = 0
        self.outputs: list[str] = []

    def read_input(self, prompt: str | None = None) -> str:
        if self._input_index < len(self.inputs):
            value = self.inputs[self._input_index]
            self._input_index += 1
            return value
        return ""

    def write_output(self, text: str) -> None:
        self.outputs.append(text)


# =============================================================================
# 辅助
# =============================================================================


def make_program_info(
    title_name: str = "《论语》",
    title_statements: list[StatementInfo] | None = None,
    chapters: list[FunctionInfo] | None = None,
) -> ProgramInfo:
    return ProgramInfo(
        FunctionInfo(title_name, title_statements or [], {}),
        chapters or [],
    )


# =============================================================================
# Program — 基本功能
# =============================================================================


class TestProgramBasic:
    """Program 基本功能的单元测试。"""

    def test_get_running_初始为None(self):
        assert Program.get_running() is None

    def test_run_期间_get_running可用(self):
        """在程序运行时，get_running() 返回当前 Program 实例。"""
        captured_program = []

        info = make_program_info("《测试》", [
            # 在书名函数中记录自身（通过一个能触发的语句来模拟）
        ])

        # 构造一个简单的验证程序：通过 run 将 self 传出
        class VerifyingProgram(Program):
            def run(self):
                super().run()
                captured_program.append(Program.get_running())

        prog = VerifyingProgram(info, MockIO())
        prog.run()
        # run 结束后 _running 应重置为 None
        assert Program.get_running() is None

    def test_run_结束后_running重置(self):
        info = make_program_info()
        prog = Program(info, MockIO())
        prog.run()
        assert Program.get_running() is None

    def test_run_结束后_global_context重置(self):
        info = make_program_info()
        prog = Program(info, MockIO())
        prog.run()
        with pytest.raises(AssertionError):
            prog.get_global_context()

    def test_get_function_info_按名称查找(self):
        """通过名称（不含书名号）查找 FunctionInfo。"""
        info = ProgramInfo(
            FunctionInfo("《论语》", [], {}),
            [
                FunctionInfo("《学而》", [], {}),
                FunctionInfo("《为政》", [], {}),
            ],
        )
        prog = Program(info, MockIO())
        assert prog.get_function_info("论语") is info.title_function
        assert prog.get_function_info("学而") is info.chapter_functions[0]
        assert prog.get_function_info("为政") is info.chapter_functions[1]

    def test_get_function_info_不存在的名称(self):
        info = make_program_info()
        prog = Program(info, MockIO())
        assert prog.get_function_info("不存在的篇章") is None

    def test_get_io_strategy(self):
        io = MockIO()
        prog = Program(make_program_info(), io)
        assert prog.get_io_strategy() is io


# =============================================================================
# Program — 端到端集成测试
# =============================================================================


class TestProgramIntegration:
    """端到端测试：从源码翻译到执行。"""

    def test_变量定义和输出(self):
        """测试基本的变量定义和输出。"""
        source = "《论语》甲子数十。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["十"]

    def test_整数运算和输出(self):
        """测试整数运算。"""
        source = "《论语》甲子数十。乙子数三。甲子益乙子。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["十三"]

    def test_字符串定义_独立(self):
        source = "《论语》甲子云hello。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["hello"]

    def test_字符串定义_搭配(self):
        source = "《论语》甲子文作hello。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["hello"]

    def test_布尔定义和判零判正(self):
        """布尔变量定义、判零、判正，然后输出。"""
        source = "《论语》甲子判曰然。甲子虚。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        # 甲子初始为 True，判零后变为 False（因为 True != 零），输出"否"
        assert io.outputs == ["否"]

    def test_赋值语句(self):
        source = "《论语》甲子数十。乙子数零。乙子取甲子。乙子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["十"]

    def test_列表操作(self):
        """测试列表定义、追加、索引修改。"""
        source = "《论语》列子举言甲、乙。新子云丙。列子接新子。列子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["甲、乙、丙"]

    def test_输入语句(self):
        """测试输入语句（变量优先语法：甲子问<提示>）。"""
        source = "《论语》甲子云默认。甲子问请输入。甲子言。"
        info = translate_program(source)
        io = MockIO(inputs=["用户输入"])
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["用户输入"]

    def test_输入整数解析(self):
        """输入时根据变量原类型进行解析。"""
        source = "《论语》甲子数零。甲子问请输入数字。甲子言。"
        info = translate_program(source)
        io = MockIO(inputs=["一百二十三"])
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["一百二十三"]

    def test_输入布尔解析(self):
        source = "《论语》甲子判曰否。甲子问输入。甲子言。"
        info = translate_program(source)
        io = MockIO(inputs=["是"])
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["是"]

    def test_条件if语句(self):
        """测试条件 if 语句。"""
        source = "《论语》条件子判曰是。若条件子是则行《学而》。甲子云书名。甲子言。《学而》乙子云篇章执行。乙子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert "篇章执行" in io.outputs
        assert "书名" in io.outputs

    def test_条件if语句_假不执行(self):
        """条件为 False 时跳过章节函数。"""
        source = "《论语》条件子判曰否。若条件子是则行《学而》。甲子云未调用篇章。甲子言。《学而》乙子云不该出现。乙子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert "未调用篇章" in io.outputs
        assert "不该出现" not in io.outputs

    def test_函数调用语句(self):
        """测试通过甲子行《...》直接调用函数。"""
        source = "《论语》甲子云书名。甲子行《学而》。甲子言。《学而》乙子云篇章。乙子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["篇章", "书名"]

    def test_全局变量在篇章间共享(self):
        """书名函数中定义的变量可在篇章函数中访问和修改。"""
        source = "《论语》共享子数十。共享子行《修改》。《修改》共享子益共享子。共享子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["二十"]

    def test_局部变量不污染全局(self):
        """篇章函数中对已有全局变量的赋值写回全局。"""
        source = "《论语》共享子数十。新值子数二十。共享子行《遮蔽》。《遮蔽》共享子取新值子。共享子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert "二十" in io.outputs

    def test_浮点数定义和输出(self):
        source = "《论语》甲子度曰三又一秒四厘。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["三又一秒四厘"]

    def test_列表删尾删头(self):
        source = "《论语》列子举言甲、乙、丙。列子削。列子斩。列子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        # 删尾→[甲,乙]，删头→[乙]
        assert io.outputs == ["乙"]

    def test_判零后条件分支(self):
        """判零的结果（布尔值）可用于 if 条件。"""
        source = "《论语》甲子数零。甲子虚。若甲子是则行《为零》。甲子数十。甲子虚。若甲子是则行《为非零》。乙子云结束。乙子言。《为零》丙子云是零。丙子言。《为非零》丁子云非零。丁子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert "是零" in io.outputs
        assert "非零" not in io.outputs
        assert "结束" in io.outputs

    def test_计算赋值_字符串连接(self):
        source = "《论语》甲子云Hello。乙子云World。甲子益乙子。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["HelloWorld"]

    def test_列表索引修改(self):
        source = "《论语》列子举言甲、乙、丙。新子云丁。列子易其二曰新子。列子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["甲、丁、丙"]

    def test_文字性语句被静默跳过(self):
        """文学性语句不影响程序正常执行。"""
        source = "《论语》此句无关紧要。甲子数十。此句也无关紧要。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["十"]

    def test_空程序(self):
        """空程序不抛出异常。"""
        source = ""
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()  # 不抛异常
        assert io.outputs == []

    def test_纯文学的_仅文学语句的程序(self):
        """仅包含文学语句（无操作）的程序。"""
        source = "《论语》春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == []

    def test_不存在的函数调用_静默跳过(self):
        """调用不存在的函数时不抛出异常。"""
        source = "《论语》甲子数十。甲子行《不存在的篇章》。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["十"]

    def test_未定义的变量输出_静默跳过(self):
        """输出未定义的变量不抛异常。"""
        source = "《论语》未定义子言。甲子数十。甲子言。"
        info = translate_program(source)
        io = MockIO()
        prog = Program(info, io)
        prog.run()
        # "未定义子言"被静默跳过，只有"甲子言"输出
        assert io.outputs == ["十"]

    def test_输入非法整数_变量变NONE(self):
        """输入非法整数字面量时变量变为 NONE。"""
        source = "《论语》甲子数零。甲子问输入。甲子言。"
        info = translate_program(source)
        io = MockIO(inputs=["不是数字"])
        prog = Program(info, io)
        prog.run()
        assert io.outputs == ["无"]
