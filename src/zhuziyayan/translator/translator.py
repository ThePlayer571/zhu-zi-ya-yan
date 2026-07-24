import re

from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo
from zhuziyayan.translator.statement_info import StatementInfo
from zhuziyayan.translator.utils import next_full_function, extract_annotation_bodies, \
    next_statement, extract_annotation_definitions


def translate_function(function_name: str, function_body: str) -> FunctionInfo:
    """将函数名和函数体解析为 FunctionInfo。

    约定：调用方保证 function_body 不含任何空白字符。

    边界情况：

    - 如果 function_name 为空，回退为 "《无名》"。
    - 如果 function_body 为空，返回的 statements 为空列表。

    Args:
        function_name: 函数名（包括《和》），例如 "《学而》"。
        function_body: 函数体源码，不含任何空白字符。

    Returns:
        FunctionInfo: 包含函数名、语句列表及注解字典的解析结果。
    """
    if not function_name:
        function_name = "《无名》"

    # 提取注解，保留注释定义于源码中
    function_body, annotations = extract_annotation_bodies(function_body)

    # 逐语句切分，记录注释定义，构建 StatementInfo
    statement_infos: list[StatementInfo] = []
    while function_body:
        statement, function_body = next_statement(function_body)
        clean_stmt, annotation_ids = extract_annotation_definitions(statement)
        statement_infos.append(StatementInfo(clean_stmt, annotation_ids))

    return FunctionInfo(function_name, statement_infos, annotations)


def translate_program(source_code: str) -> ProgramInfo:
    """将源代码翻译为 ProgramInfo。

    清除所有空白字符后，提取书名函数和篇章函数列表。

    不主动抛出任何异常——任意输入均能返回合法的 ProgramInfo。

    边界情况：

    - 如果 source_code 为空字符串或仅含空白字符，返回以 "《无名》" 为书名函数的空 ProgramInfo。
    - 如果仅有一个函数（无后续篇章），chapter_functions 为空列表。
    - 如果函数名缺失（无《》），跳过该函数体。

    Args:
        source_code: 原始源代码字符串，可含任意空白字符。

    Returns:
        ProgramInfo: 包含书名函数和篇章函数列表的解析结果。
    """
    # 清除所有空白字符
    source_code = re.sub(r'\s+', '', source_code)

    # 提取书名函数
    title_function_name, title_function_body, source_code = next_full_function(source_code)

    if not title_function_name:
        return ProgramInfo(FunctionInfo("《无名》", [], {}), [])

    title_function_info = translate_function(title_function_name, title_function_body)

    chapter_function_infos: list[FunctionInfo] = []

    # 提取篇章函数
    while True:
        chapter_function_name, chapter_function_body, source_code = next_full_function(source_code)
        if not chapter_function_name:
            break

        chapter_function_infos.append(
            translate_function(chapter_function_name, chapter_function_body))

    return ProgramInfo(title_function_info, chapter_function_infos)
