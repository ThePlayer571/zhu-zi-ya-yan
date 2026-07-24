import re
from typing import AbstractSet

import zhuziyayan.constants as constants
from zhuziyayan.translator.function_info import FunctionInfo
from zhuziyayan.translator.program_info import ProgramInfo
from zhuziyayan.translator.statement_info import StatementInfo
from zhuziyayan.utils import next_keywords


def next_function_name(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个函数名。

    边界情况：

    - 如果 source_code 为空，返回 ("", "")。
    - 如果没有找到开括号 '《'，返回 ("", "")。
    - 如果找到开括号但找不到对应的闭括号 '》'，返回 ("", "")。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, str]: (full_match, after) 元组。

            full_match 是匹配到的子串（包括《和》），例如 '《fn》'。

            after 是函数名之后的剩余源代码。
    """
    # 空字符串直接返回两空串
    if not source_code:
        return "", ""

    # 找到第一个开括号的位置
    start = source_code.find(constants.LEFT_BOOK_TITLE)
    if start == -1:
        # 未找到开括号：full_match 为空
        return "", ""

    # 从开括号之后寻找第一个闭括号
    end = source_code.find(constants.RIGHT_BOOK_TITLE, start + 1)
    if end == -1:
        # 找到开括号但没有闭括号：视为未匹配
        return "", ""

    # end_index 指向闭括号后的第一个位置（用于切片）
    end_index = end + 1
    full = source_code[start:end_index]
    after = source_code[end_index:]
    return full, after


def next_statement(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个语句。

    规则：采集第一个语句终止符之前的所有内容（包括符号）。

    边界情况：

    - 如果 source_code 为空，返回 ("", "")。
    - 如果没有找到任何语句结束符号（。？！），返回 ("", "")。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, str]: (full_match, after) 元组。

            full_match 是匹配到的语句子串（包括结尾标点。？！）。

            after 是语句之后的剩余源代码。
    """
    # 空字符串直接返回两空串
    if not source_code:
        return "", ""

    # 查找第一个语句结束符号的位置
    positions = ((d, source_code.find(d)) for d in constants.STATEMENT_TERMINATORS)
    # 过滤掉未找到的（find 返回 -1），取最小位置
    found = [(d, p) for d, p in positions if p != -1]

    if not found:
        # 没有找到任何语句结束符号：没有匹配到语句
        return "", ""

    # 取位置最靠前的结束符号
    delim, end = min(found, key=lambda x: x[1])
    end_index = end + len(delim)
    full_match = source_code[:end_index]
    after = source_code[end_index:]
    return full_match, after

def next_full_function(source_code: str) -> tuple[str, str, str]:
    """从源代码中采集第一个完整函数（函数名 + 函数体）。

    先解析函数名《...》，再将其后直到下一个《之前的所有内容作为函数体。

    边界情况：

    - 如果 source_code 为空，返回 ("", "", "")。
    - 如果找不到函数名（无《...》），返回 ("", "", "")。
    - 如果函数名后无更多《（即这是最后一个函数），body 为剩余全部内容，after 为空。
    - 如果函数体为空（函数名后紧跟《），body 为空，after 从下一个《开始。

    Args:
        source_code: 源代码字符串，不含任何空白字符。

    Returns:
        tuple[str, str, str]: (name, body, after) 元组。

            name 是完整的函数名（包括《和》），例如 '《学而》'。

            body 是函数体内容（函数名之后、下一个函数名之前的所有语句）。

            after 是函数体之后的剩余源代码，其首字符为《（若存在下一个函数）或为空。
    """

    # 解析函数名
    function_name, source_code = next_function_name(source_code)

    if not function_name:
        return "", "", ""

    # 解析函数体：跳过函数调用中的《...》，找到真正的函数定义边界
    # 函数调用《的前一个字符为行/践/施/修/用
    search_start = 0
    while True:
        pos = source_code.find(constants.LEFT_BOOK_TITLE, search_start)
        if pos == -1:
            # 没有更多《，剩余全部为函数体
            return function_name, source_code, ""
        if pos == 0:
            # 《在开头 → 真正的函数边界，函数体为空
            return function_name, "", source_code
        # 检查《的前一个字符是否是函数调用关键字
        if source_code[pos - 1] in constants.FUNCTION_CALL_KEYWORDS:
            # 这是函数调用中的《...》，跳过
            close_pos = source_code.find(constants.RIGHT_BOOK_TITLE, pos + 1)
            if close_pos == -1:
                # 没有对应的》，函数体到此为止
                return function_name, source_code[:pos], source_code[pos:]
            search_start = close_pos + 1
            continue
        # 非函数调用的《 → 真正的函数边界
        return function_name, source_code[:pos], source_code[pos:]


def extract_annotation_bodies(source_code: str) -> tuple[str, dict[str, str]]:
    """从源代码中提取所有注解（【标识符：内容】），返回清理后的源码和注解字典。

    扫描源码中所有【...】对：
    如果内容含全角冒号：→ 注解，从源码移除，加入返回字典；
    如果不含：→ 注释定义，保留在原位。

    边界情况：

    - 如果 source_code 为空，返回 ("", {})。
    - 如果【后找不到对应的】，保留【原字符，不视为注释。
    - 注解内容中如果出现：，仅第一个：作为标识符分隔符。

    Args:
        source_code: 源代码字符串。

    Returns:
        tuple[str, dict[str, str]]: (cleaned_source, annotations) 元组。

            cleaned_source 是移除所有注解后的源码，注释定义（【标识符】）保留。

            annotations 是注解字典，键为标识符，值为注解内容。
    """
    if not source_code:
        return "", {}

    annotations: dict[str, str] = {}
    result_parts: list[str] = []
    i = 0

    while i < len(source_code):
        if source_code[i] == constants.LEFT_ANNOTATION:
            # 查找对应的右括号
            j = source_code.find(constants.RIGHT_ANNOTATION, i + 1)
            if j == -1:
                # 未找到闭合括号：保留原字符
                result_parts.append(source_code[i])
                i += 1
                continue

            inner = source_code[i + 1:j]
            if constants.ANNOTATION_SEPARATOR in inner:
                # 注解：解析标识符和内容
                sep_idx = inner.index(constants.ANNOTATION_SEPARATOR)
                ann_id = inner[:sep_idx]
                ann_content = inner[sep_idx + 1:]
                annotations[ann_id] = ann_content
                # 注解从源码移除（不加入 result_parts）
            else:
                # 注释定义：完整保留（包括【】）
                result_parts.append(source_code[i:j + 1])

            i = j + 1
        else:
            result_parts.append(source_code[i])
            i += 1

    return ''.join(result_parts), annotations


def extract_annotation_definitions(statement: str) -> tuple[str, list[str]]:
    """从单条语句中提取注释定义（【标识符】），返回清理后的语句和标识符列表。

    扫描语句中所有【...】对，提取标识符并从语句文本中移除【标识符】。

    边界情况：

    - 如果 statement 为空，返回 ("", [])。
    - 如果【后找不到对应的】，保留【原字符，不视为注释。
    - 如果【...】内含：，视为注解残留，仍按定义处理（提取全部内容为标识符）。

    Args:
        statement: 单条语句字符串。

    Returns:
        tuple[str, list[str]]: (cleaned_statement, annotation_ids) 元组。

            cleaned_statement 是移除所有【标识符】后的纯语句文本。

            annotation_ids 是注释定义标识符列表，按出现顺序排列。
    """
    if not statement:
        return "", []

    ids: list[str] = []
    result_parts: list[str] = []
    i = 0

    while i < len(statement):
        if statement[i] == constants.LEFT_ANNOTATION:
            j = statement.find(constants.RIGHT_ANNOTATION, i + 1)
            if j == -1:
                # 未找到闭合括号：保留原字符
                result_parts.append(statement[i])
                i += 1
                continue

            ann_id = statement[i + 1:j]
            ids.append(ann_id)
            # 移除该注释定义（不加入 result_parts）
            i = j + 1
        else:
            result_parts.append(statement[i])
            i += 1

    return ''.join(result_parts), ids