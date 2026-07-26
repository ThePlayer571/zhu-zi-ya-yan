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
        """解析并执行函数体内的所有语句，同时记录执行过程到 Recorder。

        Statement.run() 可能返回函数名，此时由本方法负责创建并执行子函数。
        这确保了记录顺序：调用语句记录 → 子函数进入/执行/退出。

        Raises:
            RuntimeError: Program 实例不存在时抛出。
        """
        from zhuziyayan.program_system.program import Program
        from zhuziyayan.program_system.recorder import RecordEntry

        program = Program.get_running()
        if program is None:
            raise RuntimeError("Program 实例不存在，无法执行函数")
        recorder = program.recorder

        # 记录函数进入
        recorder.record(RecordEntry(
            statement_description=f"进入函数{self._info.name}",
            change="",
            statement_name="起章",
            details={"函数名": self._info.name},
            annotations=dict(self._info.annotations),
        ))

        # 逐条执行语句
        for statement_info in self._info.statements:
            program.increment_statement_count()

            statement: Statement = statement_decider.decide(
                statement_info, self._context
            )
            call_request: str | None = statement.run()

            desc, change = statement.describe()
            # 解析注释：从 FunctionInfo.annotations 按 annotation_ids 查找
            annotations: dict[str, str] = {}
            for ann_id in statement_info.annotation_ids:
                content = self._info.annotations.get(ann_id)
                if content is not None:
                    annotations[ann_id] = content

            # 记录语句执行
            recorder.record(RecordEntry(
                statement_description=desc,
                change=change,
                statement_name=statement.name,
                source_code=statement_info.statement,
                details=statement.details,
                annotations=annotations,
            ))

            # 处理函数调用请求：由上层负责创建并执行子函数
            if call_request is not None:
                function_info = program.get_function_info(call_request)
                if function_info is not None:
                    func = Function(function_info, program.get_global_context())
                    func.execute()

        # 记录函数退出
        recorder.record(RecordEntry(
            statement_description=f"退出函数{self._info.name}",
            change="",
            statement_name="毕章",
            details={"函数名": self._info.name},
            annotations=dict(self._info.annotations),
        ))
