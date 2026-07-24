from __future__ import annotations

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.function import Function
from zhuziyayan.program_system.io_strategy import IOStrategy
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo


class Program:
    """程序运行的环境。

    单例模式——同时只允许运行一个程序。。
    """

    _running: Program | None = None

    def __init__(self, program_info: ProgramInfo, io_strategy: IOStrategy):
        self._program_info: ProgramInfo = program_info
        self._io_strategy: IOStrategy = io_strategy
        self._global_context: Context | None = None

    @classmethod
    def get_running(cls) -> Program | None:
        """返回当前正在运行的 Program 实例。"""
        return cls._running

    def get_io_strategy(self) -> IOStrategy:
        """返回当前运行程序的 IO 策略。"""
        return self._io_strategy

    def get_global_context(self) -> Context:
        """返回当前运行程序的全局 Context（书名函数的 Context）。

        Raises:
            AssertionError: 在程序未运行时访问。
        """
        assert self._global_context is not None, (
            "global_context is only available while a program is running"
        )
        return self._global_context

    def get_function_info(self, name: str) -> FunctionInfo | None:
        """按函数名查找 FunctionInfo。

        Args:
            name: 函数名（不含《》书名号）。

        Returns:
            对应的 FunctionInfo；若未找到则返回 None。
        """
        full_name = f"《{name}》"
        if self._program_info.title_function.name == full_name:
            return self._program_info.title_function
        for info in self._program_info.chapter_functions:
            if info.name == full_name:
                return info
        return None

    def run(self):
        """执行程序。

        创建书名函数并以 None 为 external_context（根作用域）。
        书名函数的 Context 作为全局 Context，供篇章函数访问全局变量。
        """
        Program._running = self
        title_function = Function(self._program_info.title_function, None)
        self._global_context = title_function.context
        try:
            title_function.execute()
        finally:
            Program._running = None
            self._global_context = None
