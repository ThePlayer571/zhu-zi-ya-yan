from __future__ import annotations

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.statement import Statement
from zhuziyayan.translator.function_info import FunctionInfo
import zhuziyayan.program_system.statement_decider as statement_decider


class Function:
    """函数。

    封装一个函数的信息和执行上下文。执行时逐条解析并运行语句。
    """

    def __init__(
        self,
        function_info: FunctionInfo,
        external_context: Context | None,
    ):
        self._info: FunctionInfo = function_info
        self._context: Context = Context(external_context)

    @property
    def info(self) -> FunctionInfo:
        """该函数对应的 FunctionInfo。"""
        return self._info

    @property
    def context(self) -> Context:
        """该函数的执行上下文。"""
        return self._context

    def execute(self):
        """解析并执行函数体内的所有语句。"""
        for statement_info in self._info.statements:
            statement: Statement = statement_decider.decide(
                statement_info, self._context
            )
            statement.run()
