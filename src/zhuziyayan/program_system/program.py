from __future__ import annotations

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.function import Function
from zhuziyayan.program_system.io_strategy import IOStrategy
from zhuziyayan.program_system.recorder import Recorder
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo


class StatementLimitExceededError(Exception):
    """语句执行数超过上限时抛出。"""

    def __init__(self, limit: int):
        self.limit = limit
        super().__init__(f"语句执行数超过上限 {limit}，可能存在死循环，已强制停止。")


class Program:
    """程序运行的环境。

    单例模式——同时只允许运行一个程序。
    """

    _running: Program | None = None

    def __init__(self, program_info: ProgramInfo, io_strategy: IOStrategy,
                 max_statements: int | None = None):
        self._program_info: ProgramInfo = program_info
        self._io_strategy: IOStrategy = io_strategy
        self._global_context: Context | None = None
        self._recorder: Recorder = Recorder()
        self._max_statements: int | None = max_statements
        self._statement_count: int = 0

    @classmethod
    def get_running(cls) -> Program | None:
        """返回当前正在运行的 Program 实例。"""
        return cls._running

    @property
    def recorder(self) -> Recorder:
        """代码复盘记录器。"""
        return self._recorder

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

    def increment_statement_count(self):
        """递增语句执行计数，若超过上限则抛出 StatementLimitExceededError。

        上限为 None 时不做任何检查（默认禁用）。
        """
        if self._max_statements is None:
            return
        self._statement_count += 1
        if self._statement_count > self._max_statements:
            raise StatementLimitExceededError(self._max_statements)

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
