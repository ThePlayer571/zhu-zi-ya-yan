from zhuziyayan.program_system.context import Context
from zhuziyayan.interpreter.function_info import FunctionInfo


class Function:
    def __init__(self, function_info: FunctionInfo, context: Context):
        self._info = function_info
        self._context = context

    @property
    def info(self) -> FunctionInfo:
        return self._info

    def execute(self, global_context: Context):
        """在给定的全局上下文中执行该函数。

        创建局部上下文，解析并执行函数体内的所有语句。

        当前为占位实现，待语句解析器完成后替换。
        """
        local_context = Context(global_context=global_context)
        # TODO: 当语句解析器实现后，替换为：
        # for stmt_info in self._info.statements:
        #     stmt = parse_statement(stmt_info.statement, local_context)
        #     stmt.run()
        raise NotImplementedError(
            f"函数 '{self._info.name}' 的语句解析器尚未实现"
        )
