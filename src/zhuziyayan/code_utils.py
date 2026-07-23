import constants


def next_function_name(source_code: str) -> tuple[str, str]:
    """采集 source_code 中的第一个函数名。

    :returns:
    - full_match：匹配到的子串（包括《和》），例如 '《fn》'。
    - after：函数名之后的剩余源代码。

    边界情况：

    - 如果 source_code 为空，返回 ("", "")。

    - 如果没有找到开括号 '《'，返回 ("", "")。

    - 如果找到开括号但找不到对应的闭括号 '》'，则将从开括号到字符串末尾视为 full_match，
      返回 ("", "")。
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

    规则：采集第一个 。？！之前的所有内容（包括符号）。

    :returns:
    - full_match：匹配到的语句子串（包括结尾标点。？！）。
    - after：语句之后的剩余源代码。

    边界情况：
    - 如果 source_code 为空，返回 ("", "")。
    - 如果没有找到任何语句结束符号（。？！），返回 ("", "")。
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