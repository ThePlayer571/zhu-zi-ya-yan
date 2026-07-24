"""测试 zhuziyayan.program_system.io_strategy — IOStrategy 和 PythonNativeIO。"""

import sys
from io import StringIO
from zhuziyayan.program_system.io_strategy import PythonNativeIO


class TestPythonNativeIO:
    """PythonNativeIO 的单元测试。"""

    def test_write_output(self):
        """write_output 调用 print 输出文本。"""
        io = PythonNativeIO()
        captured = StringIO()
        sys.stdout = captured
        try:
            io.write_output("测试输出")
        finally:
            sys.stdout = sys.__stdout__
        assert captured.getvalue().strip() == "测试输出"

    def test_read_input_no_prompt(self, monkeypatch):
        """read_input 无提示读取输入。"""
        io = PythonNativeIO()
        monkeypatch.setattr("builtins.input", lambda: "测试输入")
        result = io.read_input()
        assert result == "测试输入"

    def test_read_input_with_prompt(self, monkeypatch):
        """read_input 有提示时先 print 提示再读取。"""
        io = PythonNativeIO()
        monkeypatch.setattr("builtins.input", lambda: "回答")

        captured = StringIO()
        sys.stdout = captured
        try:
            result = io.read_input("请输入：")
        finally:
            sys.stdout = sys.__stdout__

        assert result == "回答"
        assert "请输入：" in captured.getvalue()
