from zhuziyayan.interpreter.function_info import FunctionInfo
from zhuziyayan.interpreter.program_info import ProgramInfo
from zhuziyayan.interpreter.statement_info import StatementInfo
from zhuziyayan.interpreter.utils import (
    next_function_name,
    next_statement,
    extract_annotation_bodies,
    extract_annotation_definitions,
)


class Interpreter:

    def __init__(self, source_code: str):
        self._source_code: str = source_code
        self._program_info: ProgramInfo = self._interpret_program(source_code)

    @staticmethod
    def _interpret_function(function_source: str) -> FunctionInfo:
        """将一段函数体源码解析为 FunctionInfo。

        约定：调用方保证 function_source 不含任何空白字符。

        边界情况：

        - 如果函数名解析失败（name 为空），抛出 ValueError。

        Args:
            function_source: 待解析的函数体源码，不含任何空白。

        Returns:
            FunctionInfo: 包含函数名、语句列表及注解字典的解析结果。
        """
        # 1. 提取函数名
        name, function_source = next_function_name(function_source)

        if name == "":
            raise ValueError("函数名解析失败，缺少完整的函数名定义。请确保函数名使用《和》包裹。")

        # 2. 提取注解，保留注释定义于源码中
        function_source, annotations = extract_annotation_bodies(function_source)

        # 3. 逐语句切分，记录注释定义，构建 StatementInfo
        statement_infos: list[StatementInfo] = []
        while function_source:
            statement, function_source = next_statement(function_source)
            clean_stmt, annotation_ids = extract_annotation_definitions(statement)
            statement_infos.append(StatementInfo(clean_stmt, annotation_ids))

        return FunctionInfo(name, statement_infos, annotations)

    @staticmethod
    def _interpret_program(source_code: str) -> ProgramInfo:
        pass
